"""
An example that uses Portia's BrowserTool to authenticate a user against the LinkedIn website,
after which the session is used to extract information from the site.
It also shows more fine-grained control of the plan run's control flow.

This example uses a local instance of Chrome by default.
Please close Chrome before running this example so that it can be opened with the required debug settings.

If you have a paid Browserbase account,
you can switch to the `browserbase_browser_tool`,
which will execute the information extraction using the Browserbase API instead of the local browser.
"""

from dotenv import load_dotenv
from portia import (
    ActionClarification,
    Config,
    InputClarification,
    MultipleChoiceClarification,
    PlanRunState,
    Portia,
    StorageClass,
)
from portia._unstable.browser_tool import (
    BrowserInfrastructureOption,
    BrowserTool,
)

load_dotenv()

task = "Find my connections called 'Bob' on LinkedIn (https://www.linkedin.com)"

my_config = Config.from_default(storage_class=StorageClass.CLOUD)


local_browser_tool = BrowserTool(
    infrastructure_option=BrowserInfrastructureOption.LOCAL
)

# Needs Browserbase API Key.
# Not used by default - swap this for local_browser_tool in the tools list.
browserbase_browser_tool = BrowserTool(
    infrastructure_option=BrowserInfrastructureOption.BROWSERBASE
)

# Also see BrowserToolForUrl("https://www.linkedin.com")

portia = Portia(config=my_config, tools=[local_browser_tool])

plan_run = portia.run(task)

while plan_run.state == PlanRunState.NEED_CLARIFICATION:
    # If clarifications are needed, resolve them before resuming the workflow
    print("\nPlease resolve the following clarifications to continue")
    for clarification in plan_run.get_outstanding_clarifications():
        # Usual handling of Input and Multiple Choice clarifications
        if isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
            print(f"{clarification.user_guidance}")
            user_input = input(
                "Please enter a value:\n"
                + (
                    str(clarification.options)
                    if isinstance(clarification, MultipleChoiceClarification)
                    else ""
                ),
            )
            plan_run = portia.resolve_clarification(clarification, user_input, plan_run)

        # Handling of Action clarifications
        if isinstance(clarification, ActionClarification):
            print(f"{clarification.user_guidance} -- Please click on the link below to proceed.")
            print(clarification.action_url)
            input("Press Enter to continue...")

    # Once clarifications are resolved, resume the workflow
    plan_run = portia.resume(plan_run)