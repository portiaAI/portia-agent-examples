"""Simple Example."""

from portia.config import Config, LogLevel, StorageClass
from portia.execution_context import execution_context
from portia.open_source_tools.registry import example_tool_registry
from portia.plan_run import PlanRunState
from portia.portia import Portia

portia = Portia(
    Config.from_default(storage_class=StorageClass.CLOUD),
    tools=example_tool_registry,
)


# Simple Example
plan_run = portia.run_query(
    "Get the temperature in London and Sydney and then add the two temperatures rounded to 2DP",
)

# We can also provide additional execution context to the process
with execution_context(end_user_id="123", additional_data={"email_address": "hello@portialabs.ai"}):
    plan = portia.run_query(
        "Get the temperature in London and Sydney and then add the two temperatures rounded to 2DP",
    )

# When we hit a clarification we can ask our end user for clarification then resume the process
with execution_context(end_user_id="123", additional_data={"email_address": "hello@portialabs.ai"}):
    plan_run = portia.run_query(
        "Get the temperature in London and Sydney and then add the two temperatures rounded to 2DP",
    )

# Fetch run
plan_run = portia.storage.get_plan_run(plan_run.id)
print("got here")
# Update clarifications
if plan_run.state == PlanRunState.NEED_CLARIFICATION:
    for c in plan_run.get_outstanding_clarifications():
        # Here you prompt the user for the response to the clarification
        # via whatever mechanism makes sense for your use-case.
        new_value = "Answer"
        plan_run = portia.resolve_clarification(
            plan_run=plan_run,
            clarification=c,
            response=new_value,
        )

# Execute again with the same execution context
with execution_context(context=plan_run.execution_context):
    portia.execute_plan_run(plan_run)
