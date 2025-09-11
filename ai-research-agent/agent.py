import os
import sys
from dotenv import load_dotenv
from portia import (
    Config,
    DefaultToolRegistry,
    LogLevel,
    PlanRunState,
    Portia,
)
from portia.cli import CLIExecutionHooks
from pydantic import BaseModel, Field
from podcast_tool import PodcastTool

load_dotenv()

class ResearchAgentOutput(BaseModel):
    new_post_text: str = Field(
        ...,
        description=("The text that was sent to the #ai-news slack channel."),
    )

def run_agent() -> ResearchAgentOutput:
    """Run the AI research agent."""
    config = Config.from_default(
        default_model="openai/gpt-4o",
        default_log_level=LogLevel.DEBUG,
    )
    tools = DefaultToolRegistry(config) + [PodcastTool()]
    portia = Portia(
        config=config,
        tools=tools,
        execution_hooks=CLIExecutionHooks(),
    )

    # We plan and run the agent in separate steps so we can print out the plan.
    # An alternative would be to just call portia.run() which will do both.
    plan = portia.plan(
        "Read all emails from today that contain 'AI'. If there are no emails, exit. "
        "If there are emails, summarise them into a single, coherent summary (i.e. don't summarise each email separately). "
        "The summary should be focussed on 3 key themes, with each having a text summary and then a bullet-pointed list (up to 3 bullets) associated with each theme with web pages (title + link) for people to investigate further. "
        "The heading should be 'Daily AI News Update' and the summary should be in a format suitable for sending on slack / discord (i.e. no markdown formatting)."
        "For this step, when calling the llm_tool, use templating to pass the emails in (rather than copying them verbatim)."
        "Then post the summary with links to the slack channel with ID C08D31BNFGV. "
        "Then, create a short podcast based on the emails, driven by the summary but with further details coming from the emails. "
        "For this step, when calling the podcast tool, use templating to pass the emails in (rather than copying them verbatim)."
    )

    print("\nHere are the steps in the generated plan:")
    print(plan.pretty_print())

    if os.getenv("CI") != "true":
        user_input = input("Are you happy with the plan? (y/n):\n")
        if user_input != "y":
            sys.exit(1)

    run = portia.run_plan(
        plan,
        structured_output_schema=ResearchAgentOutput,
    )

    if run.state != PlanRunState.COMPLETE:
        raise Exception(
            f"Plan run failed with state {run.state}. Check logs for details."
        )
    return ResearchAgentOutput.model_validate(run.outputs.final_output.value)


if __name__ == "__main__":
    run_agent()
