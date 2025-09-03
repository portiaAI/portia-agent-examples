"""
The same task2 example as 2_tools_end_users_llms.py, but using a PlanBuilder to build the plan.

Required configuration:

- `PORTIA_API_KEY`
- `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`)
- To run task2 (default):
    - `TAVILY_API_KEY`
"""

from dotenv import load_dotenv
from portia import (
    Config,
    DefaultToolRegistry,
    PlanBuilderV2,
    Portia,
    StepOutput,
    StorageClass,
    open_source_tool_registry,
)
from portia.cli import CLIExecutionHooks

load_dotenv()

plan = (
    PlanBuilderV2()
    .single_tool_agent_step(
        task="Add 1 + 1",
        tool="calculator_tool",
    )
    .final_output(output_schema=FinalPlanOutput)
    .build()
)

plan = (
    PlanBuilderV2()
    .single_tool_agent_step(
        step_name="amazon_stock_price",
        task="Find the growth of Amazon's stock price since the start of 2024",
        tool="search_tool",
    )
    .single_tool_agent_step(
        step_name="google_stock_price",
        task="Find the growth of Google's stock price since the start of 2024",
        tool="search_tool",
    )
    .llm_step(
        task="Determine which company has grown more since the start of 2024",
        inputs=[StepOutput("amazon_stock_price"), StepOutput("google_stock_price")],
    )
    .build()
)

# Needs Tavily API key
plan2 = (
    PlanBuilderV2()
    # Start our plan by using the Tavily search tool to search the web for the gold price in the last 30 days
    .invoke_tool_step(
        step_name="research_gold_price",
        args={"search_query": "gold price in the last 30 days"},
        tool="search_tool",
    )
    # Then us an LLM to create a report on the gold price using the search results
    .llm_step(
        step_name="analyze_gold_price",
        task="Write a report on the gold price in the last 30 days",
        # We can pass in the search results using StepOutput
        inputs=[StepOutput("research_gold_price")],
    )
    # Finally we use an agent with
    .single_tool_agent_step(
        step_name="send_email",
        task="Send the report about gold price to bob@portialabs.ai",
        inputs=[StepOutput("analyze_gold_price")],
        tool="send_email_tool",
    )
    .build()
)

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
plan_run = portia.run_plan(plan2, end_user="its me, mario")
