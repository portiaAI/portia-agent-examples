import json
from datetime import datetime
from dotenv import load_dotenv
from portia import Portia, Config, DefaultToolRegistry, ToolRegistry, default_config
from portia.cli import CLIExecutionHooks
from custom_tools import luma_events, meetup_events

load_dotenv(override=True)

with open('data.json', 'r') as file:
    data = json.load(file)
    recipient_interest = data['recipient_interest']
    recipient_location = data['recipient_location']
    recipient_email = data['recipient_email']
    no_of_events = data['no_of_events']
    recipient_name = data['recipient_name']

today = datetime.now().date().isoformat()
interest_text = ", ".join(recipient_interest) if isinstance(recipient_interest, (list, tuple)) else str(recipient_interest)

default_registry = DefaultToolRegistry(default_config())
events_tool_registry = ToolRegistry([luma_events(), meetup_events()])

all_tools = default_registry + events_tool_registry
portia = Portia(config = Config.from_default(),
    tools = all_tools,
    execution_hooks=CLIExecutionHooks(),)

# TASK 1: Luma Events Discovery
task_1_luma = f"""
TASK 1: LUMA EVENTS DISCOVERY (multi-interest capable)

Analyze the user interest "{recipient_interest}". If it contains multiple interests
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

Process the location "{recipient_location}" to determine the ISO 3166-1 alpha-2 country code.

PROCEDURE:
1) Parse interests from "{recipient_interest}" into a unique set (trim, lowercase for matching).
2) For EACH mapped category (deduplicated):
   - Call the luma_events tool with:
     • url: the category URL above
     • location: the processed location data
3)Filter results for events in the next 3 months and return in standardized format.
4)Concatenate results from ALL calls into 'luma_results' for later aggregation.
"""


# TASK 2: Meetup Events Discovery  
task_2_meetup = f"""
TASK 2: MEETUP EVENTS DISCOVERY

Transform the user interest "{recipient_interest}" for Meetup URL compatibility:
- Replace spaces with '+' signs
- Handle special characters appropriately
- Example: "machine learning" → "machine+learning"

Construct Meetup search URL: https://www.meetup.com/find/?events=&keywords={{transformed_keywords}}&source=EVENTS

Process the location "{recipient_location}" to determine the ISO 3166-1 alpha-2 country code.

Call the meetup_events tool with:
- url: The constructed Meetup search URL
- location: The processed location data

Filter results for events in the next 3 months and return in standardized format.
Store results as 'meetup_results' for later aggregation.
"""

# TASK 3: Event Filtering and Aggregation
task_3_filter = f"""
TASK 3: EVENT FILTERING AND AGGREGATION

Combine the results from luma_results and meetup_results.

Apply intelligent filtering:
1. Remove duplicates (same event on multiple platforms)
2. Filter for events happening in/near "{recipient_location}" in the next 3 months
3. Rank by relevance to "{recipient_interest}" using semantic matching
4. Rank by proximity to {recipient_location}
5. Ensure temporal variety across the 3-month period

Select the top {no_of_events} most relevant events with good distribution across:
- Different dates/weeks
- Mix of platforms (Luma/Meetup)
- High relevance scores

Return final curated list as 'final_events'.
"""

# TASK 4: Email Creation and Sending (enforce signature, add newsletter styling)
task_4_email = f"""
TASK 4: EMAIL CREATION AND SENDING

Create a professional HTML email to {recipient_email}.

Subject: Top {interest_text} Events in {recipient_location} — Next 3 Months

FORMAT (STRICT, NEWSLETTER STYLE):
- Indicate the source implicitly via the button text “Register on Meetup” or “Register on Luma”.
- Use an ordered list <ol> for the events inside the main body; each event is one <li>.
- Inside each <li>, render lines in this exact order (one <br> per line):
  <strong>[Event Name] — [City], [Country Code]</strong><br>
  Description: [2–3 concise sentences]<br>
  Location: [Venue / exact location]<br>
  Date: [DD/MM/YYYY]<br>
  Time: [HH:MM]<br>
  <a href="[URL]" Register on [Platform]</a><br>
- Labels must appear exactly as: Description, Location, Date, Time, Register on [Platform].
- Events must be ordered chronologically (earliest first).
- Keep consistent punctuation and spacing. One <li> per event, no extra blank lines needed.
- Return RAW HTML ONLY. Do not include Markdown code fences or any backticks. 
- Never output ```html or ``` anywhere.

CONTENT (STRICT):
- Greeting (first line in the body): Hi {recipient_name},
- Reference their interests and location using: "{interest_text}" and {recipient_location}.
- Add a brief (1–2 sentence) explanation of how the events were selected.
- Include exactly {no_of_events} events (if fewer exist, include all available and explicitly state that).
- Close with a short call-to-action.

SIGNATURE (MUST MATCH EXACTLY):
- After the body content, place this exact signature in the footer area:
  Best regards,<br>
  Portia Meetup & Luma Event Curator
  

TBD / PLACEHOLDERS:
- Do not mix undated or placeholder items into the numbered list.
- If any exist, append a separate section after the <ol>:>
  <ul>
    <li><strong>[Event Name] — [City], [Country Code]</strong> • <a href="[URL]" >Register on [Platform]</a></li>
  </ul>

DELIVERY:
- Send the email using the available email-sending tool.
- After sending, return a brief confirmation that includes the provider’s send status (e.g., message ID).
"""


# Execute all tasks in sequence
full_task = f"""
Execute these 4 tasks in sequence:

{task_1_luma}

{task_2_meetup}

{task_3_filter}

{task_4_email}

Each task should complete successfully before moving to the next. Store intermediate results between tasks for proper data flow.
"""

portia.run(query=full_task)