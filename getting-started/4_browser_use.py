"""
An example that uses Portia's BrowserTool to authenticate a user against the LinkedIn website,
after which the session is used to extract information from the site.
It also shows more fine-grained control of the plan run's control flow.

This example uses a local instance of Chrome by default.
Please close Chrome before running this example so that it can be opened with the required debug settings.

If you have a paid Browserbase account, you can switch to the `browserbase_browser_tool`,
which will execute the information extraction using the Browserbase API instead of the local browser.
"""

from dotenv import load_dotenv
from portia import (
    Config,
    Portia,
    StorageClass,
)
from portia.cli import CLIExecutionHooks
from portia.open_source_tools.browser_tool import (
    BrowserInfrastructureOption,
    BrowserTool,
)

load_dotenv()

task = (
    "Find my connections called 'Bob' on LinkedIn (https://www.linkedin.com)"
)

my_config = Config.from_default(storage_class=StorageClass.CLOUD)


local_browser_tool = BrowserTool(
    infrastructure_option=BrowserInfrastructureOption.LOCAL
)

# Needs Browserbase API Key and a paid account.
# Not used by default - swap this for local_browser_tool in the tools list when configuring Portia.
browserbase_browser_tool = BrowserTool(
    infrastructure_option=BrowserInfrastructureOption.REMOTE
)

# Also see BrowserToolForUrl("https://www.linkedin.com")

portia = Portia(
    config=my_config,
    tools=[local_browser_tool],
    execution_hooks=CLIExecutionHooks(),
)

plan_run = portia.run(task)
