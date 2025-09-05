from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from portia.cli import CLIExecutionHooks
from custom_tools import luma_events, meetup_events, create_typeform, EventSchema, EventsSchema
from portia import Portia, Config, DefaultToolRegistry, ToolRegistry, default_config, PlanBuilderV2, StepOutput, Input


class FinalOutput(BaseModel):
    final_events: List[EventSchema] = Field(..., description="Curated short list of events")
    form_url: Optional[str] = Field(None, description="URL to a form for RSVP or feedback")

class EventDiscoveryAgent:
    """
    Discovers events from Luma & Meetup, curates them, and creates a Typeform.
    This version *manually builds* the plan using PlanBuilderV2.
    """
    def __init__(self, recipient_interest: List[str] | str, recipient_location: str, no_of_events: int, recipient_name: str, has_form: bool = False,) -> None:
        load_dotenv(override=True)
        self.recipient_interest = recipient_interest
        self.recipient_location = recipient_location
        self.no_of_events = int(no_of_events)
        self.recipient_name = recipient_name
        self.has_form = has_form
        self.today = datetime.now().date().isoformat()

        # Portia + tools
        self._setup_portia()

    def _setup_portia(self) -> None:
        default_registry = DefaultToolRegistry(default_config())

        self.luma_tool = luma_events()
        self.meetup_tool = meetup_events()
        self.typeform_tool = create_typeform()

        events_tool_registry = ToolRegistry([self.luma_tool, self.meetup_tool, self.typeform_tool])
        all_tools = default_registry + events_tool_registry
        self.portia = Portia(config=Config.from_default(), tools=all_tools, execution_hooks=CLIExecutionHooks())

    def _build_plan(self):
        """
        Plan:
          1) Search Luma
          2) Search Meetup
          3) Combine + filter to a curated list containing {{self.no_of_events}} events
          4) Conditionally create a Typeform
          5) Final structured output
        """
        builder = (
            PlanBuilderV2("Discover events and (optionally) create a form")
            .input(name="recipient_interest", description="User interests (string or list)")
            .input(name="recipient_location", description="Location of interest for events")
            .input(name="no_of_events", description="Max number of curated events to return")
            .input(name="recipient_name", description="Name of the recipient")
            .input(name="today", description="Today in YYYY-MM-DD")
            .input(name="has_form", description="If true, create a Typeform")
            
            .single_tool_agent_step(task=("""Analyze the user interest "{self.recipient_interest}". If it contains multiple interests
            (comma), split them and handle EACH interest separately.

            CATEGORY MAPPING (choose exactly ONE per interest):
            - AI, Arts & Culture, Climate, Fitness, Wellness, Crypto

            CATEGORY → URL:
            - AI → https://lu.ma/ai
            - Arts & Culture → https://lu.ma/arts
            - Climate → https://lu.ma/climate
            - Fitness → https://lu.ma/fitness
            - Wellness → https://lu.ma/wellness
            - Crypto → https://lu.ma/crypto

            Process the location "{self.recipient_location}" to determine the ISO 3166-1 alpha-2 country code.

            PROCEDURE:
            1) Parse interests from "{self.recipient_interest}" into a unique set (trim, lowercase for matching).
            2) For EACH mapped category (deduplicated):
            - Call the luma_events tool with:
                • url: the category URL above
                • location: the processed location data
            3) Filter results for events in the next 3 months from {self.today} and return in standardized format.
            4) Concatenate results from ALL calls into 'luma_results' for later aggregation."""),
            tool="luma_events",
            inputs=[Input("recipient_interest"), Input("recipient_location"), Input("today")],)
            
            .single_tool_agent_step(task=("""Transform the user interest "{self.recipient_interest}" for Meetup URL compatibility:
                - Replace spaces with '+' signs
                - Handle special characters appropriately
                - Example: "machine learning" → "machine+learning"
                - 

                Construct Meetup search URL: https://www.meetup.com/find/?events=&keywords={{transformed_keywords}}&source=EVENTS

                Process the location "{self.recipient_location}" to determine the ISO 3166-1 alpha-2 country code.

                Call the meetup_events tool with:
                - url: The constructed Meetup search URL
                - location: The processed location data

                Filter results for events in the next 3 months from {self.today} and return in standardized format.
                Store results as 'meetup_results' for later aggregation.
                """),
            tool="meetup_events",
            inputs=[Input("recipient_interest"), Input("recipient_location"), Input("today")],)
            
            
            .llm_step(task=f"""You will receive two RAW event lists (arbitrary JSON) as inputs:
            - Input[0]: Luma raw
            - Input[1]: Meetup raw

            GOAL
            Return a single shortlist of at most {self.no_of_events} events.

            FILTER (both sources)
            - Keep events located in/near "{self.recipient_location}".
            - Date range: {self.today} .. {self.today} + 90 days (inclusive).

            DEDUPLICATION (cross-source)
            - Two items are the same if (after lowercasing & stripping punctuation/extra spaces):
            - names are very similar AND dates equal; OR
            - event_url host+path are the same (ignore tracking params like utm_*, ref, ?fbclid).

            RANKING
            - Primary: semantic relevance to "{self.recipient_interest}".
            - Secondary: proximity to {self.recipient_location}.
            - Tertiary: temporal variety (spread across different weeks)"""
            .strip(),
            inputs=[StepOutput(0), StepOutput(1)],output_schema=EventsSchema)
            
            .if_(condition=lambda has_form: has_form, args={"has_form": Input("has_form")})
            .single_tool_agent_step(tool="create_typeform",
                task=("Create a Typeform that lists the curated events and captures RSVP/interest. "
                    "Use recipient_name to personalise where possible. "
                    "Return ONLY the public form URL as form_url in FinalOutput."),
                inputs=[StepOutput(2), Input("recipient_name")],
            ).endif())

        # 5) Final output (names now match FinalOutput fields, so mapping is trivial)
        plan = builder.final_output(output_schema=FinalOutput).build()
        return plan

    def run(self) -> FinalOutput:
        plan = self._build_plan()
        plan_run = self.portia.run_plan(
            plan,
            plan_run_inputs={
                "recipient_interest": self.recipient_interest,
                "recipient_location": self.recipient_location,
                "no_of_events": self.no_of_events,
                "recipient_name": self.recipient_name,
                "today": self.today,
                "has_form": self.has_form,
            },
        )
        return plan_run.outputs.final_output.value
