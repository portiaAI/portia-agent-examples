from dotenv import load_dotenv
from portia import (
    Config,
    LLMModel,
    PlanRunState,
    Portia,
    execution_context,
)
from portia.cli import CLIExecutionHooks

load_dotenv()

my_config = Config.from_default(
    llm_model_name=LLMModel.GPT_4_O,
)

# Instantiate a Portia instance. Load it with the default config and with the example tools.
portia = Portia(config=my_config, execution_hooks=CLIExecutionHooks())

with execution_context(
    end_user_id="portia-research-agent",
):
    # We plan and run the agent in separate steps so we can print out the plan.
    # An alternative would be to just call portia.run() which will do both.
    plan = portia.plan(
        "Read all emails from today that contain 'AI' and summarise them. "
        "Then post the summary with links to the #ai-news channel."
    )
    print(plan)
    run = portia.run_plan(plan)

    if run.state != PlanRunState.COMPLETE:
        raise Exception(
            f"Plan run failed with state {run.state}. Check logs for details."
        )
