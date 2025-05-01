"""
An example showing how Portia OAuth works when authentication is required.

This example will print a URL to the console and wait until authentication is completed in the browser before continuing.

Required configuration:

- `PORTIA_API_KEY`
- `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`)
"""

from dotenv import load_dotenv
from portia import (
    Config,
    Portia,
    PortiaToolRegistry,
    StorageClass,
)
from portia.cli import CLIExecutionHooks

load_dotenv()

# A relatively simple task:
task0 = "Star the github repo for portiaAI/portia-sdk-python"

# A more complex task:
task1 = """
Check my availability in Google Calendar for tomorrow between 10am and 12pm.
If I have any free times between 10am and 12pm, please schedule a 30-minute meeting with
bob (bob@portialabs.ai) with title 'Encode Hackathon', and description 'hack it'.
If I don't have any free times, please output the next time after 12pm when I am free.
"""

# Instantiate a Portia runner. Load it with the default config and with Portia cloud tools above.
# Use the CLIExecutionHooks to allow the user to handle any clarifications at the CLI.
my_config = Config.from_default(storage_class=StorageClass.CLOUD)
portia = Portia(
    config=my_config,
    tools=PortiaToolRegistry(my_config),
    execution_hooks=CLIExecutionHooks(),
)

# Change `task0` to `task1` to execute a more complex task.
plan_run = portia.run(task0)
print(plan_run.outputs)
