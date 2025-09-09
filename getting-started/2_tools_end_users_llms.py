"""
An example demonstrating the use of execution_context to provide the user id of the end-user.

Required configuration:

- `PORTIA_API_KEY`
- `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`)
- To run task2 (default):
    - `TAVILY_API_KEY`
- To run task3 (requires code change):
    - `OPENWEATHERMAP_API_KEY`
"""

from dotenv import load_dotenv
from portia import (
    Config,
    DefaultToolRegistry,
    Portia,
    StorageClass,
    open_source_tool_registry,
)
from portia.cli import CLIExecutionHooks

load_dotenv()

# Needs Tavily API key
task2 = (
    "Research the price of gold in the last 30 days, "
    "and send bob@portialabs.ai a report about it."
)

# Needs OpenWeatherMap API key
task3 = "Fetch the weather in London and email bob@portialabs.ai with the results."


# Instantiate a Portia runner. Load it with the default config and with Portia cloud tools above.
# Use the CLIExecutionHooks to allow the user to handle any clarifications at the CLI.
my_config = Config.from_default(storage_class=StorageClass.CLOUD)

portia = Portia(
    config=my_config,
    tools=DefaultToolRegistry(my_config) + open_source_tool_registry,
    execution_hooks=CLIExecutionHooks(),
)

# This plan will ask the user to authenticate against Google Mail.
#
# Within Portia's system,
# the authentication token will be stored for the `end_user_id` below.
# Repeated runs of this script won't require re-authentication,
# unless the `end_user_id` is changed to a different value.
# Change `task2` to `task3` to fetch a weather report:
plan_run = portia.run(task2, end_user="its me, mario")
