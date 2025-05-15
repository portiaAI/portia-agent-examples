"""
An example that makes use of an MCP server to obtain a tool for fetching web content.

The MCP server used is: https://github.com/modelcontextprotocol/servers/tree/main/src/fetch

Required configuration:

- `PORTIA_API_KEY`
- `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`)
"""

from dotenv import load_dotenv
from portia import (
    Config,
    DefaultToolRegistry,
    McpToolRegistry,
    Portia,
    StorageClass,
)
from portia.cli import CLIExecutionHooks

load_dotenv()

task = "Read the portialabs.ai website and tell me what they do"

my_config = Config.from_default(storage_class=StorageClass.CLOUD)

# Install and run an MCP server for fetching web pages.
# https://github.com/modelcontextprotocol/servers/tree/main/src/fetch
registry = McpToolRegistry.from_stdio_connection(
    server_name="fetch",
    command="uvx",
    args=["mcp-server-fetch"],
) + DefaultToolRegistry(my_config)

portia = Portia(
    config=my_config,
    tools=registry,
    execution_hooks=CLIExecutionHooks(),
)

print(portia.run(task).outputs.final_output)
