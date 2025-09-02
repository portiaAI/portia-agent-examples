from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from dotenv import load_dotenv

from portia import Config, DefaultToolRegistry, PlanBuilderV2, PlanRun, Portia, StepOutput
from portia.cli import CLIExecutionHooks


def _tomorrow_window() -> tuple[str, str]:
    """Return ISO8601 start/end for tomorrow 10:00-17:00 local time."""
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    start = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    end = tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)
    return start.isoformat(), end.isoformat()


def build_plan() -> PlanBuilderV2:
    """Create a plan that checks calendar availability, schedules a meeting, and emails details.

    Uses single-tool agent steps so Portia can handle tool argument planning, clarifications,
    and Google auth flows via CLIExecutionHooks.
    """
    start_iso, end_iso = _tomorrow_window()

    return (
        PlanBuilderV2("Schedule meeting and email details")
        .user_input(
            message="Enter the recipient's email address for the meeting invite and follow-up: ",
            step_name="Get Recipient Email",
        )
        .user_input(
            message="Enter a meeting title (default: 'Portia AI Demo'): ",
            step_name="Get Meeting Title",
        )
        .user_input(
            message="Enter a short meeting description (default: 'Test demo'): ",
            step_name="Get Meeting Description",
        )
        .single_tool_agent_step(
            tool="portia:google:gcalendar:check_availability",
            task=(
                f"Check my Google Calendar availability tomorrow between {start_iso} and {end_iso}. "
                "Return a list of open 30-minute slots."
            ),
            step_name="Check Availability",
        )
        .single_tool_agent_step(
            tool="portia:google:gcalendar:create_event",
            task=(
                "Using the availability from the previous step, schedule a 30 minute meeting with "
                f"{StepOutput('Get Recipient Email')} at the earliest suitable time. "
                f"Use the title from {StepOutput('Get Meeting Title')} (default 'Portia AI Demo' if empty) "
                f"and description from {StepOutput('Get Meeting Description')} (default 'Test demo' if empty). "
                "Include the recipient as a guest."
            ),
            step_name="Create Event",
        )
        .user_verify(
            message=(
                "About to send an email confirmation with the event details. Proceed? "
                f"Event ref: {StepOutput('Create Event')}"
            ),
            step_name="Confirm Email Send",
        )
        .single_tool_agent_step(
            tool="portia:google:gmail:send_email",
            task=(
                "Send an email to the recipient with the details of the meeting that was just scheduled. "
                f"To: {StepOutput('Get Recipient Email')}. "
                f"Subject: Meeting scheduled - use {StepOutput('Get Meeting Title')} (default 'Portia AI Demo'). "
                "Body: Include date/time, attendees, and calendar link from the created event."
            ),
            step_name="Send Email",
        )
        .final_output(summarize=True)
    )


async def main() -> PlanRun:
    load_dotenv(override=True)

    # Configure Portia with default cloud tools (includes Google tools) and CLI clarifications.
    cfg = Config.from_default()
    portia = Portia(config=cfg, tools=DefaultToolRegistry(cfg), execution_hooks=CLIExecutionHooks())

    plan = build_plan().build()
    return await portia.arun_plan(plan)


if __name__ == "__main__":
    result = asyncio.run(main())
    print(result.model_dump_json(indent=2))

