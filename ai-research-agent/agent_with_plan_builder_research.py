import os
import sys
import json
from datetime import datetime

from dotenv import load_dotenv
from portia import (
    Config,
    DefaultToolRegistry,
    Input,
    LogLevel,
    PlanBuilderV2,
    PlanRunState,
    Portia,
    StepOutput,
    StorageClass,
)
from portia.cli import CLIExecutionHooks
from pydantic import BaseModel, Field
from podcast_tool import PodcastTool

load_dotenv()


class EmailSummary(BaseModel):
    """Summary of AI-related emails."""

    title: str = Field(..., description="Title for the daily AI news update")
    summary: str = Field(
        ..., description="Coherent summary focused on 3 key themes with bullet points"
    )
    theme_count: int = Field(..., description="Number of key themes identified")
    has_emails: bool = Field(..., description="Whether any AI-related emails were found")


class ResearchAgentOutput(BaseModel):
    """Final output from the research agent."""

    new_post_text: str = Field(
        ..., description="The text that was sent to the #ai-news slack channel"
    )
    podcast_location: str = Field(..., description="Location of the generated podcast file")
    emails_processed: int = Field(..., description="Number of emails processed")


def check_emails_exist(emails_content) -> bool:
    """Check if any emails were found."""
    # Handle both list and string inputs from Gmail API
    if isinstance(emails_content, str):
        try:
            parsed = json.loads(emails_content)
            if isinstance(parsed, list):
                return len(parsed) > 0
        except json.JSONDecodeError:
              print("Not valid JSON")
              # Handle as regular string
              return (len(emails_content.strip()) > 0 and
                      "no emails found" not in emails_content.lower())
    elif isinstance(emails_content, list):
          return len(emails_content) > 0

    return False

def run_agent() -> ResearchAgentOutput:
    """Run the AI research agent using PlanBuilderV2."""

    config = Config.from_default(
        default_model="openai/gpt-4o",
        default_log_level=LogLevel.DEBUG,
        storage_class=StorageClass.CLOUD,
    )
    
    # Add our custom podcast tool to the Portia cloud tools registry
    tools = DefaultToolRegistry(config) + [PodcastTool()]
    
    portia = Portia(
        config=config,
        tools=tools,
        execution_hooks=CLIExecutionHooks(),
    )

    # Build the plan using PlanBuilderV2
    plan = (
        PlanBuilderV2("AI Research Agent - Email Summary and Podcast Generator")
        .input(
            name="date_filter",
            description="Date to filter emails (defaults to today's date)",
            default_value=datetime.now().strftime("%Y-%m-%d")
        )
        .input(
            name="slack_channel_id", 
            description="Slack channel ID for posting updates",
            default_value=os.getenv("SLACK_CHANNEL_ID")
        )
        
        # Step 1: Read emails from Gmail about AI
        .single_tool_agent_step(
            step_name="fetch_ai_emails",
            tool="portia:google:gmail:search_email",
            task=f"Search for emails from today ({Input('date_filter')}) that contain 'AI' in the subject or body. If no emails are found, return 'no emails found'.",
            inputs=[Input("date_filter")],
        )

        .if_(
            condition=lambda emails_content: not check_emails_exist(emails_content),
            args={"emails_content": StepOutput("fetch_ai_emails")},
        )

        .function_step(
            step_name="exit_no_emails",
            function=lambda: (_ for _ in ()).throw(SystemExit("No AI emails found for today. Exiting now.")),
        )
        
        .endif()
        
        # Step 2: Create summary using LLM with templating
        .llm_step(
            step_name="create_summary",
            task="Create a coherent summary of the AI-related emails. Focus on 3 key themes, with each having a text summary and then a bullet-pointed list (up to 3 bullets) with web pages (title + link) for further investigation. Use the heading 'Daily AI News Update' and format for Slack/Discord (no markdown formatting). Use templating to reference the emails efficiently rather than copying them verbatim.",
            inputs=[StepOutput("fetch_ai_emails")],
            output_schema=EmailSummary,
        )
        
        # Step 3: Post summary to Slack
        .single_tool_agent_step(
            step_name="post_to_slack",
            tool="portia:slack:bot:send_message",
            task=f"Send the AI news summary to slack channel {Input('slack_channel_id')}",
            inputs=[StepOutput("create_summary"), Input("slack_channel_id")],
        )
        
        # Step 4: Generate podcast using our custom tool
        .invoke_tool_step(
            step_name="generate_podcast",
            tool="podcast_tool",
            args={
                "summary": StepOutput("create_summary"),
                "details": StepOutput("fetch_ai_emails"),
            },
        )
        
        # Here's the configuration of the final outtput
        .final_output(
            output_schema=ResearchAgentOutput,
            summarize=True,
        )
        .build()
    )

    print("\nGenerated Plan Structure:")
    print(plan.pretty_print())

    if os.getenv("CI") != "true":
        user_input = input("Are you happy with the plan? (y/n): ")
        if user_input.lower() != "y":
            sys.exit(1)

    # Execute the plan
    run = portia.run_plan(
        plan,
        plan_run_inputs={
            "date_filter": datetime.now().strftime("%Y-%m-%d"),
            "slack_channel_id": os.getenv("SLACK_CHANNEL_ID")
        },
    )

    if run.state != PlanRunState.COMPLETE:
        raise Exception(
            f"Plan run failed with state {run.state}. Check logs for details."
        )

    return ResearchAgentOutput.model_validate(run.outputs.final_output.value)

if __name__ == "__main__":
    try:
        result = run_agent()
        print(f"\nAgent completed successfully!")
        print(f"Processed {result.emails_processed} emails")
        print(f"Posted summary: {result.new_post_text[:100]}")
        print(f"Podcast saved to: {result.podcast_location}")
    except Exception as e:
        print(f"Agent failed: {e}")
        sys.exit(1)