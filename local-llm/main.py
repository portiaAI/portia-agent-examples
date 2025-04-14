import os
from dotenv import load_dotenv
from portia import (
    Config,
    LLMTool,
    McpToolRegistry,
    Portia,
    ToolRegistry,
)
from portia.cli import CLIExecutionHooks
import portia.tool

portia.tool.MAX_TOOL_DESCRIPTION_LENGTH = 2048


def main():
    config = Config.from_default(
        default_log_level="DEBUG",
        planning_model="openai/o3-mini",
        default_model="ollama/qwen2.5:14b",
    )
    obsidian_mcp = McpToolRegistry.from_stdio_connection(
        server_name="obsidian",
        command="npx",
        args=["-y", "obsidian-mcp", os.getenv("OBSIDIAN_VAULT_PATH")],
    )

    portia = Portia(
        config=config,
        execution_hooks=CLIExecutionHooks(),
        tools=obsidian_mcp + ToolRegistry([LLMTool()]),
    )
    plan = portia.plan(
        "Using my portia-agent-vault Obsidian vault, find my note about the hackathon and summarise it",
        example_plans=[],
    )
    print(plan.pretty_print())
    portia.run_plan(plan)


if __name__ == "__main__":
    load_dotenv()
    main()
