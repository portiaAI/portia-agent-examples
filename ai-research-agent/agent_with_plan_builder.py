"""
A command-line script that generates concept maps of Obsidian notes using PlanBuilderV2.

It interfaces with Obsidian through MCP and uses a vibe-coded visualization
tool to generate concept maps based on the content of specified notes.
"""

import argparse
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../local-llm"))
)

from dotenv import load_dotenv
from portia import (
    Config,
    ExecutionAgentType,
    McpToolRegistry,
    Portia,
    ToolRegistry,
    PlanBuilderV2,
    Input,
    StepOutput,
)

from tools.visualization_tool import VisualizationTool


def create_plan_local(portia: Portia, note_name: str):
    """
    Create a predefined plan for generating a concept map from an Obsidian note using PlanBuilderV2.

    This function builds a plan with specific steps to:
    1. List available Obsidian vaults
    2. Fetch the specified note
    3. Create a concept map visualization from the note's content

    Args:
        portia: The Portia instance to use for plan creation and execution
        note_name: The name of the Obsidian note to visualize

    Returns:
        The created plan object
    """
    plan = (
        PlanBuilderV2(
            f"Create a concept map image from the note with title {note_name}"
        )
        .input(
            name="note_name",
            description="The name of the Obsidian note to visualize",
        )
        .single_tool_agent_step(
            step_name="List all available vaults",
            tool="mcp:obsidian:list_available_vaults",
            task="List all available vaults",
            inputs=[],
        )
        .single_tool_agent_step(
            step_name="Fetch the note",
            tool="mcp:obsidian:read_note",
            task=f"Fetch the note named '{note_name}' from the obsidian vaults",
            inputs=[Input("note_name"), StepOutput("List vaults")],
        )
        .single_tool_agent_step(
            step_name="Create concept map",
            tool="visualization_tool",
            task=f"Create a concept map visualization using the extracted relationships. Title the image {note_name} and output the image to the directory {os.getenv('OBSIDIAN_VAULT_PATH')}/visualizations",
            inputs=[StepOutput("Fetch the note")],
        )
        .build()
    )
    # Note: PlanV2 objects don't support save_plan() in the current version
    portia.storage.save_plan(plan)
    return plan


def create_plan_remote(portia: Portia, note_name: str):
    """
    Create a plan for generating a concept map using Portia's planning capabilities.

    Instead of using a predefined plan structure, this function lets Portia generate
    a plan based on a natural language query describing the task.

    Args:
        portia: The Portia instance to use for plan creation
        note_name: The name of the Obsidian note to visualize

    Returns:
        The generated plan object
    """
    query = f"""
    1. List all available vaults.
    2. Fetch the note with {note_name} from the vault.
    3. Create a concept map showing relationships between key data in the note and make sure the relationships correlate to each others. 
      - The output directory for the concept map is {os.getenv("OBSIDIAN_VAULT_PATH")}/visualizations.
    """
    return portia.plan(query)


def main(argv=sys.argv[1:]):
    """
    Main function to run this application.

    This function:
    1. Loads environment variables
    2. Parses command line arguments
    3. Sets up Portia with the necessary configuration and tools
    4. Creates and executes a plan to generate a concept map from an Obsidian note

    Args:
        argv: Command line arguments

    Raises:
        ValueError: If OBSIDIAN_VAULT_PATH environment variable is not set
    """
    load_dotenv()

    if os.getenv("OBSIDIAN_VAULT_PATH") is None:
        raise ValueError("OBSIDIAN_VAULT_PATH is not set in your environment variables")

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "note_name",
        help="The name of the note to be visualised.",
    )

    args = argument_parser.parse_args(argv)

    config = Config.from_default(
        default_log_level="DEBUG",
        default_model="ollama/qwen3:4b",
        execution_agent_type=ExecutionAgentType.ONE_SHOT,
    )
    # Make sure OBSIDIAN_VAULT_PATH is set in your environment variables
    obsidian_mcp = McpToolRegistry.from_stdio_connection(
        server_name="obsidian",
        command="npx",
        args=["-y", "obsidian-mcp", os.getenv("OBSIDIAN_VAULT_PATH")],
    )

    # Add all tools to the registry
    tools = obsidian_mcp + ToolRegistry([VisualizationTool()])

    portia = Portia(
        config=config,
        tools=tools,
    )

    plan = create_plan_local(portia, args.note_name)
    print(plan.pretty_print())
    portia.run_plan(plan)


if __name__ == "__main__":
    main()
