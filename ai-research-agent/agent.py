import os
import shutil
import sys

import yaml
from dotenv import load_dotenv
from podcastfy.client import generate_podcast
from portia import (
    Config,
    DefaultToolRegistry,
    ExecutionContext,
    InMemoryToolRegistry,
    LLMModel,
    LogLevel,
    PlanRunState,
    Portia,
    Tool,
    execution_context,
)
from portia.cli import CLIExecutionHooks
from pydantic import BaseModel, Field

load_dotenv()


class PodcastToolSchema(BaseModel):
    """Input for PodcastTool."""

    summary: str = Field(
        ...,
        description=("The high-level summary for the podcast."),
    )
    details: str = Field(
        ...,
        description=("Further details that can be used in creating the podcast."),
    )


class PodcastTool(Tool[str]):
    """Create a podcast based on a high-level summary and further details."""

    id: str = "podcast_tool"
    name: str = "Podcast Tool"
    description: str = (
        "Used to create a podcast based on a high-level summary and further details."
    )
    args_schema: type[BaseModel] = PodcastToolSchema
    output_schema: tuple[str, str] = (
        "str",
        "The location of the output audio file.",
    )

    def run(self, _: ExecutionContext, summary: str, details: str) -> str:
        """Run the Podcast Tool."""

        config_path = os.path.join(
            os.path.dirname(__file__), "conversation_config.yaml"
        )
        with open(config_path) as config_file:
            conversation_config = yaml.safe_load(config_file)

        if os.getenv("GEMINI_API_KEY"):
            llm_model_name = "gemini-1.5-pro-latest"
            api_key_label = "GEMINI_API_KEY"
            tts_model = "gemini"
            # If your GCP project has had multi-speaker allowlisted, you can use this instead:
            # tts_model = "geminimulti"
        else:
            llm_model_name = "gpt-4o"
            api_key_label = "OPENAI_API_KEY"
            tts_model = "openai"

        audio_file = generate_podcast(
            text=f"A summary of today's AI news is given by: {summary}\n\nDiving deeper, here are the full details: {details}",
            llm_model_name=llm_model_name,
            api_key_label=api_key_label,
            conversation_config=conversation_config,
            tts_model=tts_model,
        )

        # Copy the audio file to a standard location for the latest podcast
        latest_podcast_path = os.path.join(
            os.path.dirname(__file__), "data", "audio", "podcast_latest.mp3"
        )
        shutil.copy2(audio_file, latest_podcast_path)

        return latest_podcast_path


config = Config.from_default(
    llm_model_name=LLMModel.GPT_4_O,
    default_log_level=LogLevel.DEBUG,
)
tools = DefaultToolRegistry(config) + InMemoryToolRegistry.from_local_tools(
    [PodcastTool()]
)
# Instantiate a Portia instance. Load it with the default config and with the example tools.
portia = Portia(
    config=config,
    tools=tools,
    execution_hooks=CLIExecutionHooks(),
)

with execution_context(
    end_user_id="portia-research-agent",
):
    # We plan and run the agent in separate steps so we can print out the plan.
    # An alternative would be to just call portia.run() which will do both.
    plan = portia.plan(
        "Read all emails from today that contain 'AI' and summarise them into a single, coherent summary (i.e. don't summarise each email separately). "
        "Then post the summary with links to the #app-testing channel."
        "Then, create a short podcast based on the emails, driven by the summary but with further details coming from the emails."
    )
    print("\nHere are the steps in the generated plan:")
    [print(step.model_dump_json(indent=2)) for step in plan.steps]

    if os.getenv("CI") != "true":
        user_input = input("Are you happy with the plan? (y/n):\n")
        if user_input != "y":
            sys.exit(1)

    run = portia.run_plan(plan)

    if run.state != PlanRunState.COMPLETE:
        raise Exception(
            f"Plan run failed with state {run.state}. Check logs for details."
        )
