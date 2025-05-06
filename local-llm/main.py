import os
from dotenv import load_dotenv
from portia import (
    Config,
    ExecutionAgentType,
    LLMTool,
    McpToolRegistry,
    Portia,
    ToolRegistry,
)
from portia.plan import PlanBuilder
from portia.cli import CLIExecutionHooks
import portia.tool
from tools.visualization_tool import VisualizationTool

portia.tool.MAX_TOOL_DESCRIPTION_LENGTH = 2048

def create_plan_local(portia: Portia, note_name: str):
    plan = PlanBuilder(f"Create a concept map image from the note with title {note_name}") \
        .step("List all available vaults", "mcp:obsidian:list_available_vaults") \
        .step(f"Fetch the note named '{note_name}' from the obsidian vaults", "mcp:obsidian:read_note") \
        .step(f"Create a concept map visualization using the extracted relationships. Title the image {note_name} and output the image to the directory {os.getenv("OBSIDIAN_VAULT_PATH")}/visualizations", "visualization_tool") \
        .build()
    portia.storage.save_plan(plan)
    return plan

def create_plan_remote(portia: Portia, note_name: str):
    query = f"""
    1. List all available vaults.
    2. Fetch the note with {note_name} from the vault.
    3. Create a concept map showing relationships between key data in the note and make sure the relationships correlate to each others. 
      - The output directory for the concept map is {os.getenv("OBSIDIAN_VAULT_PATH")}/visualizations.
    """
    return portia.plan(query)
    

def main():
    config = Config.from_default(
        default_log_level="DEBUG",
        default_model="ollama/qwen3:4b",
        execution_agent_type=ExecutionAgentType.ONE_SHOT,
    )
    # Make sure OBSIDIAN_VAULT_PATH is set in your environment variables
    if os.getenv("OBSIDIAN_VAULT_PATH") is None:
        raise ValueError("OBSIDIAN_VAULT_PATH is not set in your environment variables")

    obsidian_mcp = McpToolRegistry.from_stdio_connection(
        server_name="obsidian",
        command="npx",
        args=["-y", "obsidian-mcp", os.getenv("OBSIDIAN_VAULT_PATH")],
    )

    visualization_tool = VisualizationTool()

    # Add all tools to the registry
    tools = obsidian_mcp + ToolRegistry([
        LLMTool(),
        visualization_tool
    ])

    portia = Portia(
        config=config,
        execution_hooks=CLIExecutionHooks(),
        tools=tools,
    )

    plan = create_plan_local(portia, "Local LLMs")
    print(plan.pretty_print())
    portia.run_plan(plan)


if __name__ == "__main__":
    load_dotenv()
    main()
