from datetime import datetime
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field
from portia.cli import CLIExecutionHooks
from custom_tools import EventsSchema
from portia.open_source_tools.browser_tool import BrowserTool, BrowserInfrastructureOption
from portia import Portia, Config, DefaultToolRegistry, ToolRegistry, default_config, PlanBuilderV2, Input

load_dotenv(override=True)

class RegistrationSchema(BaseModel):
    event_name: str = Field(..., description="The name/title of the event")
    event_date: str = Field(..., description="Date in ISO format YYYY-MM-DD")
    event_time: Optional[str] = Field(None, description="Time, ideally HH:MM in 24-hour format")
    event_location: Optional[str] = Field(None, description="Location name or city")
    event_url: str = Field(..., description="Canonical URL for the event")
    registration_status: str = Field(..., description='One of: registered|requires_payment|waitlisted|failed')
    registration_notes: Optional[str] = Field(None, description="Details about registration process")

class AttendanceSchema(BaseModel):
    events: List[RegistrationSchema]

class EventRegistrationAgent:
    """
    Registers for provided events (Meetup/Luma/etc.) via BrowserTool and
    returns the SAME output type as events_discover.py (FinalOutput).
    """
    def __init__(self, config: dict):
        self.config = config
        self._setup_portia()

    def _setup_portia(self) -> None:
        default_registry = DefaultToolRegistry(default_config())
        browser_tool = BrowserTool(infrastructure_option=BrowserInfrastructureOption.LOCAL)
        tool_registry = ToolRegistry([browser_tool])
        all_tools = default_registry + tool_registry
        self.portia = Portia(config=Config.from_default(), tools=all_tools, execution_hooks=CLIExecutionHooks(),)
        
    def _build_plan(self):
        builder = (
            PlanBuilderV2("Register for each input event with BrowserTool, then emit AttendanceSchem ")
            .input(name="events", description="List of events to register for.")
            .input(name="config",description="Personal details (name, email, phone, etc.) for filling forms.",default_value=self.config)
            .single_tool_agent_step(tool="browser_tool",task=("For each event in {events}, open the event page and attempt registration.\n"
                "Rules:\n"
                "- Loop over events and attempt to register for each event only 2ce"
                "- Prefer 'In person'. Skip events that require payment.\n"
                "- If asked to join a group: click Join/Request to join; if asked 'why', say you’re interested in learning and meeting people in the same field as you.\n"
                "- If a form appears, fill it using {config} (name/email/etc.).\n"
                "- If form requires more than what you have in {config} try to make up reasonable answers"
                "- If asked to subscribe to a news letter, only accept if there is no option to decline"
                "- After submitting, capture the exact on-page message(s) or a concise summary.\n"
                "- For each event, output: event_name, event_date, event_time, event_location, event_url, registration_status (registered|requires_payment|waitlisted|failed), registration_notes.\n"
                "Return a single AttendanceSchema containing all processed events."),
                inputs=[Input("events"), Input("config")], output_schema = AttendanceSchema,))
        plan = builder.final_output(output_schema=AttendanceSchema).build()
        return plan

    def run(self, events: EventsSchema) -> AttendanceSchema:
        plan = self._build_plan()
        plan_run = self.portia.run_plan(plan, plan_run_inputs={"events": events, "config": self.config})
        return plan_run.outputs.final_output.value
