import json, argparse
from typing import Any
from datetime import datetime
from dotenv import load_dotenv
from portia.cli import CLIExecutionHooks
from portia import Portia, Config, DefaultToolRegistry, ToolRegistry, default_config
from custom_tools import luma_events, meetup_events, create_typeform

class EventDiscoveryAgent:
    """Agent responsible for discovering and emailing curated events from Luma and Meetup."""
    
    def __init__(self, config_file: str = 'data.json'):
        """Initialize the agent with configuration from JSON file."""
        load_dotenv(override=True)
        
        # Load user data
        with open(config_file, 'r') as file:
            data = json.load(file)
            self.recipient_interest = data['recipient_interest']
            self.recipient_location = data['recipient_location']
            self.recipient_email = data['recipient_email']
            self.no_of_events = data['no_of_events']
            self.recipient_name = data['recipient_name']
        
        # Setup date and interest text
        self.today = datetime.now().date().isoformat()
        self.interest_text = ", ".join(self.recipient_interest) if isinstance(
            self.recipient_interest, (list, tuple)
        ) else str(self.recipient_interest)
        
        # Setup Portia with tools
        self._setup_portia()
    
    def _setup_portia(self) -> None:
        """Setup Portia instance with all required tools."""
        default_registry = DefaultToolRegistry(default_config())
        events_tool_registry = ToolRegistry([
            luma_events(), 
            meetup_events(), 
            create_typeform(),
        ])
        
        all_tools = default_registry + events_tool_registry
        self.portia = Portia(
            config=Config.from_default(),
            tools=all_tools,
            execution_hooks=CLIExecutionHooks(),
        )
    
    def _get_luma_task(self) -> str:
        """Generate Task 1: Luma Events Discovery."""
        return f"""
        TASK 1: LUMA EVENTS DISCOVERY (multi-interest capable)

        Analyze the user interest "{self.recipient_interest}". If it contains multiple interests
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
        4) Concatenate results from ALL calls into 'luma_results' for later aggregation.
        """
    
    def _get_meetup_task(self) -> str:
        """Generate Task 2: Meetup Events Discovery."""
        return f"""
        TASK 2: MEETUP EVENTS DISCOVERY

        Transform the user interest "{self.recipient_interest}" for Meetup URL compatibility:
        - Replace spaces with '+' signs
        - Handle special characters appropriately
        - Example: "machine learning" → "machine+learning"

        Construct Meetup search URL: https://www.meetup.com/find/?events=&keywords={{transformed_keywords}}&source=EVENTS

        Process the location "{self.recipient_location}" to determine the ISO 3166-1 alpha-2 country code.

        Call the meetup_events tool with:
        - url: The constructed Meetup search URL
        - location: The processed location data

        Filter results for events in the next 3 months from {self.today} and return in standardized format.
        Store results as 'meetup_results' for later aggregation.
        """
            
    def _get_filter_task(self) -> str:
        """Generate Task 3: Event Filtering and Aggregation."""
        return f"""
        TASK 3: EVENT FILTERING AND AGGREGATION

        Combine the results from luma_results and meetup_results.

        Apply intelligent filtering:
        1. Remove duplicates (same event on multiple platforms)
        2. Filter for events happening in/near "{self.recipient_location}" in the next 3 months starting from {self.today}
        3. Rank by relevance to "{self.recipient_interest}" using semantic matching
        4. Rank by proximity to {self.recipient_location}
        5. Ensure temporal variety across the 3-month period

        Select the top {self.no_of_events} most relevant events with good distribution across:
        - Different dates/weeks
        - Mix of platforms (Luma/Meetup)
        - High relevance scores

        Return final curated list as 'final_events' with each event containing:
        - event_name
        - event_date 
        - event_time
        - event_location
        - event_url
        """
    
    def _get_form_creation_task(self) -> str:
        """Generate Task 4: Google Form Creation."""
        return f"""
        TASK 4: TYPEFORM CREATION

        Using the 'final_events' from the previous task, create a TypeForm form for event registration preferences.

        Form Configuration:
        - Title: "Event Registration Preferences - {self.interest_text} in {self.recipient_location}"
        - Description: "Hi {self.recipient_name}! We've curated the top {self.no_of_events} events based on your interests in {self.interest_text}. Please let us know which events you'd be interested in."

        Use the create_typeform tool with:
        - title: The form title above
        - description: The form description above  
        - events: The final_events list

        The form will automatically create:
        For each event: Radio button question with options:
           - "Register me automatically" (interested_register)
           - "I'm interested but will register manually" (interested_manual)
           - "Not interested" (not_interested)

        Store the returned form_url for the email task. If there is an error return the error message as the form url.
        """
        
    def _get_email_task_without_form(self) -> str:
        """Generate Task 4: Email Creation and Sending."""
        return f"""
        TASK 4: EMAIL CREATION AND SENDING (Original)

        Create a professional HTML email to {self.recipient_email}.

        Subject: Top {self.interest_text} Events in {self.recipient_location} — Next 3 Months

        FORMAT (STRICT, NEWSLETTER STYLE):
        - Indicate the source implicitly via the button text "Register on Meetup" or "Register on Luma".
        - Use an ordered list <ol> for the events inside the main body; each event is one <li>.
        - Inside each <li>, render lines in this exact order (one <br> per line):
        <strong>[Event Name] — [City], [Country Code]</strong><br>
        Description: [2—3 concise sentences]<br>
        Location: [Venue / exact location]<br>
        Date: [DD/MM/YYYY]<br>
        Time: [HH:MM]<br>
        <a href="[URL]" Register on [Platform]</a><br>
        - Events must be ordered chronologically (earliest first).
        - Return RAW HTML ONLY.

        SIGNATURE (STRICT):
        Best regards,<br>
        Portia Meetup & Luma Event Curator

        Send the email using the available email-sending tool.
        """
        
    def _get_email_task(self) -> str:
        """Generate Task 5: Email Creation and Sending with Form."""
        return f"""
        TASK 5: EMAIL CREATION AND SENDING WITH FORM

        Create a professional newsletter style email to {self.recipient_email} that includes the curated events AND the Interest Form.

        Subject: Top {self.interest_text} Events in {self.recipient_location} — Registration Form Included

        EMAIL STRUCTURE (STRICT):

        1. GREETING:
        Hi {self.recipient_name},

        2. INTRODUCTION (2-3 sentences):
        - Reference their interests: "{self.interest_text}" and location: {self.recipient_location}
        - Explain how events were selected
        - Mention the automatic registration option

        3. EVENTS SHOWCASE (ordered list):
        Use <ol> with each event as <li>:
        <strong>[Event Name] — [City], [Country Code]</strong><br>
        Description: [2–3 concise sentences about the event]<br>
        Location: [Venue / exact location]<br>
        Date: [DD/MM/YYYY]<br>
        Time: [HH:MM]<br>
        <a href="[URL]">View Event Details on [Platform]</a><br>

        4. REGISTRATION FORM SECTION:
        <h3>🎯 Want us to register you automatically?</h3>
        <p>Fill out our quick form to let us know which events you'd like to attend:</p>
        <p><a href="[FORM_URL]">Complete Registration Form</a></p>
        If there is an error, please include the error message in the registration form.

        6. SIGNATURE:
        Best regards,<br>
        Portia Meetup & Luma Event Curator

        REQUIREMENTS:
        - Events ordered chronologically (earliest first)
        - Include the form_url from the previous task
        - Do not return markdown or HTML code fences.
        - Send using the available email-sending tool
        - Return confirmation with send status

        IMPORTANT: Replace [FORM_URL] with the actual form_url from Task 4.
        """
    
    def run_full_discovery(self) -> Any:
        """Execute all tasks in sequence including form creation."""
        print("Starting full event discovery process with Google Form integration...")
        
        full_task = f"""
        Execute these 5 tasks in sequence:

        {self._get_luma_task()}

        {self._get_meetup_task()}

        {self._get_filter_task()}

        {self._get_form_creation_task()}

        {self._get_email_task()}

        Each task should complete successfully before moving to the next. Store intermediate results between tasks for proper data flow. Ensure you strictly follow the rules in each task for optimal results.
        """
            
        result = self.portia.run(query=full_task)
        return result
    
    def run_discovery_only(self) -> Any:
        """Execute only event discovery without form creation (original functionality)."""
        print("Starting event discovery process (without form)...")
        
        discovery_task = f"""
        Execute these 4 tasks in sequence:

        {self._get_luma_task()}

        {self._get_meetup_task()}

        {self._get_filter_task()}
        
        {self._get_email_task_without_form()}
        """
        
        result = self.portia.run(query=discovery_task)
        return result



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-form', '-f',action='store_true',help='Include Form creation for automatic registration preferences')
    parser.add_argument('--config', '-c', default='data.json',help='Path to configuration JSON file (default: data.json)')
    args = parser.parse_args()
    
    agent = EventDiscoveryAgent(config_file=args.config)
    
    if args.with_form:
        print("Running event discovery WITH Google Form integration...")
        result = agent.run_full_discovery()
    else:
        print("Running event discovery WITHOUT form (email only)...")
        result = agent.run_discovery_only()