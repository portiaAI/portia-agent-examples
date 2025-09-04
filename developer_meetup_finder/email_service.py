from dotenv import load_dotenv
from portia.cli import CLIExecutionHooks
from portia import Portia, Config, DefaultToolRegistry, default_config, PlanBuilderV2, StepOutput, Input


class EmailService:
    """Service responsible for sending event-related emails with intelligent content adaptation."""
    
    def __init__(self, config):
        load_dotenv(override=True)
        self.config = config
        self._setup_portia()
    
    def _setup_portia(self) -> None:
        """Setup Portia instance with email tools."""
        default_registry = DefaultToolRegistry(default_config())
        self.portia = Portia(config=Config.from_default(),tools=default_registry,execution_hooks=CLIExecutionHooks())
    
    def send_event_email(self):
        builder = (
            PlanBuilderV2("Send event email with intelligent content based on context using Newsletter style.")
            .input(name="events", description="List of events and their registration details to send email about.")
            .input(name="config",description="Personal details (name, email, phone, etc.) for filling forms.",default_value=self.config)
            .single_tool_agent_step(tool="portia:google:gmail:send_email", task=("""INTELLIGENT EVENT EMAIL TASK
                Analyze the context and send an appropriate email to {recipient_email}:

                CONTEXT ANALYSIS:
                - Recipient: {config.recipient_name}
                - Interests: {config.recipient_interest}
                - Location: {config.recipient_location}
                - Number of events: len({self.event_details.events})
                - Has form URL: Check if {self.event_details} has a form_url key in it

                EVENTS DATA:
                {self.event_details}

                EMAIL STRATEGY (choose based on context):

                1. IF {self.event_details} has registration_status and registration_notes in them
                - Subject: "{recipient_interest} events in {recipient_location} with registration updates"
                - Focus: Event showcase + details about automatic registrations attempt
                Include Event URL
                - Include registration status for each event

                2. IF {self.event_details} has a form_url key:
                - Subject: "{num_events} curated {recipient_interest} events in {recipient_location} - Interest form included"
                - Focus: Event showcase + form for preferences
                - Include Event URL
                - Include registration preference form

                EMAIL STRUCTURE (adapt based on strategy above):

                1. GREETING: Hi {recipient_name},

                2. INTRODUCTION (2-3 sentences based on mode):
                - Reference interests and location
                - Summary of the events and registration details

                3. EVENTS SHOWCASE:
                Use <ol> with each event as <li>:
                <strong>[Event Name] — [City], [Country Code]</strong><br>
                Description: [2-3 concise sentences]<br>
                Location: [Venue/exact location]<br>
                Date: [DD/MM/YYYY]<br>
                Time: [HH:MM]<br>
                
                CONTEXT-AWARE LINKS:
                - If has_registrations: "✅ Registered" or "❌ Registration failed: [reason]"
                - <a href="[URL]">View Event Details on [Platform]</a> for all events

                4. CONTEXT-SPECIFIC SECTION:
                - If form_url exists: Include registration form section

                5. SIGNATURE:
                Best regards,<br>
                Portia Event Management System

                REQUIREMENTS:
                - Events ordered chronologically (earliest first)
                - Professional newsletter-style HTML
                - Send using available email tool
                - Return confirmation with send status
                - NO markdown code fences in output"""),
            inputs=[Input("events"), Input("config")]))
        plan =  builder.build() 
        return plan

    def run(self, event_details):
        plan = self.send_event_email()
        plan_run = self.portia.run_plan(plan, plan_run_inputs={"events": event_details, "config": self.config})
        return plan_run

