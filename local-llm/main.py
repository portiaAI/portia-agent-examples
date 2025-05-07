"""
Main module for the local-llm project.

This module provides functionality to create concept maps from Obsidian notes
using a local LLM. It interfaces with Obsidian through MCP and uses a visualization
tool to generate concept maps based on the content of specified notes.
"""

import argparse
import os
import sys

import portia.tool
from dotenv import load_dotenv
from portia import (
    Config,
    ExecutionAgentType,
    LLMTool,
    McpToolRegistry,
    Portia,
    ToolRegistry,
)
from portia.cli import CLIExecutionHooks
from portia.plan import PlanBuilder

from tools.visualization_tool import VisualizationTool

portia.tool.MAX_TOOL_DESCRIPTION_LENGTH = 2048


def create_plan_local(portia: Portia, note_name: str):
    """
    Create a predefined plan for generating a concept map from an Obsidian note.
    
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
        PlanBuilder(
            f"Create a concept map image from the note with title {note_name}"
        )
        .step(
            "List all available vaults", "mcp:obsidian:list_available_vaults"
        )
        .step(
            f"Fetch the note named '{note_name}' from the obsidian vaults",
            "mcp:obsidian:read_note",
        )
        .step(
            f"Create a concept map visualization using the extracted relationships. Title the image {note_name} and output the image to the directory {os.getenv('OBSIDIAN_VAULT_PATH')}/visualizations",
            "visualization_tool",
        )
        .build()
    )
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
    Main function to run the local-llm application.
    
    This function:
    1. Loads environment variables
    2. Parses command line arguments
    3. Sets up Portia with the necessary configuration and tools
    4. Creates and executes a plan to generate a concept map from an Obsidian note
    
    Args:
        argv: Command line arguments (defaults to sys.argv[1:])
        
    Raises:
        ValueError: If OBSIDIAN_VAULT_PATH environment variable is not set
    """
    load_dotenv()

    if os.getenv("OBSIDIAN_VAULT_PATH") is None:
        raise ValueError(
            "OBSIDIAN_VAULT_PATH is not set in your environment variables"
        )

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "note",
        help="The name of the note to be visualised.",
        default="Local LLMs",
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

    visualization_tool = VisualizationTool()

    # Add all tools to the registry
    tools = obsidian_mcp + ToolRegistry([LLMTool(), visualization_tool])

    portia = Portia(
        config=config,
        execution_hooks=CLIExecutionHooks(),
        tools=tools,
    )

    plan = create_plan_local(portia, args.note)
    print(plan.pretty_print())
    portia.run_plan(plan)


if __name__ == "__main__":
    main()
