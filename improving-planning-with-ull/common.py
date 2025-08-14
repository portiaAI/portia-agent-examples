"""
common - Boilerplate code abstracted from the scripts in this user-led learning example project.

This code is not meant to be run directly.

Primarily, this code imports a handful of tool stubs (which will be used to demonstrate planning),
and provides an `init_portia()` function which loads config from a `.env` file and configures an instance of Portia for use in scripts.
"""

import os

import portia.tool
from dotenv import load_dotenv
from mock_tools import RefundHumanApprovalTool, RefundReviewerTool
from portia import (
    Config,
    DefaultToolRegistry,
    InMemoryToolRegistry,
    McpToolRegistry,
    Portia,
)
from portia.cli import CLIExecutionHooks

portia.tool.MAX_TOOL_DESCRIPTION_LENGTH = 2048


def init_portia():
    """
    Load config from a `.env` file and return a configured instance of `Portia`.
    """

    load_dotenv(override=True)

    config = Config.from_default(default_log_level="INFO")

    tools = (
        McpToolRegistry.from_stdio_connection(
            server_name="stripe",
            command="npx",
            args=[
                "-y",
                "@stripe/mcp",
                "--tools=all",
                f"--api-key={os.environ['STRIPE_TEST_API_KEY']}",
            ],
        )
        + DefaultToolRegistry(
            config=config,
        )
        + InMemoryToolRegistry.from_local_tools(
            [RefundReviewerTool(), RefundHumanApprovalTool()]
        )
    )

    portia_instance = Portia(
        config=config, tools=tools, execution_hooks=CLIExecutionHooks()
    )

    return portia_instance
