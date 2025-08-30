import os
import shutil
import sys
from datetime import datetime
from typing import Any

import yaml
from dotenv import load_dotenv
from podcastfy.client import generate_podcast
from portia import (
    ActionClarification,
    Config,
    DefaultToolRegistry,
    Input,
    LogLevel,
    PlanBuilderV2,
    PlanRunState,
    Portia,
    StepOutput,
    StorageClass,
    Tool,
    ToolRunContext,
)
from portia.cli import CLIExecutionHooks
from pydantic import BaseModel, Field

load_dotenv()


class EmailSummary(BaseModel):
    """Summary of AI-related emails."""

    title: str = Field(..., description="Title for the daily AI news update")
    summary: str = Field(
        ..., description="Coherent summary focused on 3 key themes with bullet points"
    )
    theme_count: int = Field(..., description="Number of key themes identified")
    has_emails: bool = Field(..., description="Whether any AI-related emails were found")


class PodcastContent(BaseModel):
    """Content structure for podcast generation."""

    summary: str = Field(..., description="High-level summary for the podcast")
    details: str = Field(..., description="Detailed content for podcast creation")


class ResearchAgentOutput(BaseModel):
    """Final output from the research agent."""

    new_post_text: str = Field(
        ..., description="The text that was sent to the #ai-news slack channel"
    )
    podcast_location: str = Field(..., description="Location of the generated podcast file")
    emails_processed: int = Field(..., description="Number of emails processed")


class PodcastToolSchema(BaseModel):
    """Input for PodcastTool."""

    summary: str = Field(..., description="The high-level summary for the podcast")
    details: str = Field(..., description="Further details that can be used in creating the podcast")


class PodcastTool(Tool[str]):
    """Create a podcast based on a high-level summary and further details."""

    id: str = "podcast_tool"
    name: str = "Podcast Tool"
    description: str = "Used to create a podcast based on a high-level summary and further details."
    args_schema: type[BaseModel] = PodcastToolSchema
    output_schema: tuple[str, str] = ("str", "The location of the output audio file.")

    def run(self, _: ToolRunContext, summary: str, details: str) -> str:
        """Run the Podcast Tool."""
        config_path = os.path.join(os.path.dirname(__file__), "conversation_config.yaml")
        with open(config_path) as config_file:
            conversation_config = yaml.safe_load(config_file)

        if os.getenv("GOOGLE_API_KEY"):
            llm_model_name = "gemini-1.5-flash"
            api_key_label = "GOOGLE_API_KEY"
            tts_model = "google"
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
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(latest_podcast_path), exist_ok=True)
        shutil.copy2(audio_file, latest_podcast_path)

        return latest_podcast_path


def check_emails_exist(emails_content) -> bool:
    """Check if any emails were found."""
    # Handle both list and string inputs from Gmail API
    if isinstance(emails_content, list):
        return len(emails_content) > 0
    elif isinstance(emails_content, str):
        return emails_content.strip() != "" and "no emails" not in emails_content.lower()
    else:
        return False


def extract_email_count(emails_content) -> int:
    """Extract the number of emails from the content."""
    if not check_emails_exist(emails_content):
        return 0
    
    # Handle both list and string inputs from Gmail API
    if isinstance(emails_content, list):
        return len(emails_content)
    elif isinstance(emails_content, str):
        # Simple approach - count occurrences of common email patterns
        return max(1, emails_content.count("Subject:") + emails_content.count("From:"))
    else:
        return 0


def format_emails_for_processing(emails_content) -> str:
    """Convert Gmail API output (list or string) to a formatted string for LLM processing."""
    if isinstance(emails_content, list):
        if len(emails_content) == 0:
            return "No AI-related emails found for today."
        
        # Format each email in the list for better LLM processing
        formatted_emails = []
        for i, email in enumerate(emails_content, 1):
            if isinstance(email, dict):
                # Handle structured email data
                subject = email.get('subject', 'No subject')
                sender = email.get('from', email.get('sender', 'Unknown sender'))
                snippet = email.get('snippet', email.get('body', 'No content'))
                formatted_emails.append(f"Email {i}:\nFrom: {sender}\nSubject: {subject}\nContent: {snippet}\n")
            else:
                # Handle string representation of email
                formatted_emails.append(f"Email {i}: {str(email)}\n")
        
        return f"Found {len(emails_content)} AI-related emails:\n\n" + "\n".join(formatted_emails)
    elif isinstance(emails_content, str):
        return emails_content if emails_content.strip() else "No AI-related emails found for today."
    else:
        return "No AI-related emails found for today."


def create_podcast_content(emails: str, summary: str) -> PodcastContent:
    """Create structured content for podcast generation."""
    return PodcastContent(
        summary=summary,
        details=f"Based on today's AI emails: {emails}"
    )


def run_agent() -> ResearchAgentOutput:
    """Run the AI research agent using PlanBuilderV2."""

    portia_api_key = os.getenv("PORTIA_API_KEY")
    if not portia_api_key:
        raise ValueError("PORTIA_API_KEY environment variable is required for cloud tools")
    

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI models")
    
    config = Config.from_default(
        default_model="openai/gpt-4o",
        default_log_level=LogLevel.DEBUG,
        storage_class=StorageClass.CLOUD,
        portia_api_key=portia_api_key,
        openai_api_key=openai_api_key,
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
            description="Date to filter emails (today's date)",
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
        
        # Step 2: Check if emails exist and exit if none found
        .function_step(
            step_name="check_email_existence",
            function=check_emails_exist,
            args={"emails_content": StepOutput("fetch_ai_emails")},
        )
        
        .if_(
            condition=lambda has_emails: not has_emails,
            args={"has_emails": StepOutput("check_email_existence")},
        )
        .function_step(
            step_name="exit_no_emails",
            function=lambda: "No AI emails found for today. Exiting gracefully.",
        )
        .endif()
        
        # Step 3: Format emails for processing
        .function_step(
            step_name="format_emails",
            function=format_emails_for_processing,
            args={"emails_content": StepOutput("fetch_ai_emails")},
        )
        
        # Step 4: Count emails for tracking
        .function_step(
            step_name="count_emails",
            function=extract_email_count,
            args={"emails_content": StepOutput("fetch_ai_emails")},
        )
        
        # Step 5: Create summary using LLM with templating
        .llm_step(
            step_name="create_summary",
            task="Create a coherent summary of the AI-related emails. Focus on 3 key themes, with each having a text summary and then a bullet-pointed list (up to 3 bullets) with web pages (title + link) for further investigation. Use the heading 'Daily AI News Update' and format for Slack/Discord (no markdown formatting). Use templating to reference the emails efficiently rather than copying them verbatim.",
            inputs=[StepOutput("format_emails")],
            output_schema=EmailSummary,
        )
        
        # Step 5: Post summary to Slack
        .single_tool_agent_step(
            step_name="post_to_slack",
            tool="portia:slack:bot:send_message",
            task=f"Send the AI news summary to slack channel {Input('slack_channel_id')}",
            inputs=[StepOutput("create_summary"), Input("slack_channel_id")],
        )
        
        # Step 6: Generate podcast using our custom tool
        .invoke_tool_step(
            step_name="generate_podcast",
            tool="podcast_tool",
            args={
                "summary": StepOutput("create_summary"),
                "details": StepOutput("format_emails"),
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

    # Handle OAuth authentication for Google services
    while run.state == PlanRunState.NEED_CLARIFICATION:
        print("\n Authentication required")
        clarifications = run.get_outstanding_clarifications()
        
        for clarification in clarifications:
            if isinstance(clarification, ActionClarification):
                print(f"Please visit this URL to authenticate: {clarification.action_url}")
                print("After completing authentication, the agent will continue automatically.")
                run = portia.wait_for_ready(run)
                break
        else:
            # If no ActionClarification found, break to avoid infinite loop
            break

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