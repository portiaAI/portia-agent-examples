import os, json
from dotenv import load_dotenv
from portia import Portia, Config, DefaultToolRegistry
from portia.cli import CLIExecutionHooks

load_dotenv(override=True)

with open('recipient_data.json', 'r') as file:
    data = json.load(file)
    recipient_interest = data['recipient_interest']
    recipient_location = data['recipient_location']
    recipient_email = data['recipient_email']

config = Config.from_default()
portia = Portia(config=config,
    tools=DefaultToolRegistry(config=config),
    execution_hooks=CLIExecutionHooks(),)

# TASK 1: Scrape Luma Events
task_luma = f"""
Please scrape Luma events for my interest:

USER PROFILE:
- Interest: {recipient_interest}
- Location: {recipient_location}

STEP 1: Classify and Scrape Luma Events
- Classify the user interest "{recipient_interest}" into ONE of these Luma categories: AI, Arts & Culture, Climate, Fitness, Wellness, Crypto
- Use the appropriate category URL from: https://lu.ma/ai, https://lu.ma/arts, https://lu.ma/climate, https://lu.ma/fitness, https://lu.ma/wellness, https://lu.ma/crypto
- Use firecrawl with: formats=["markdown"], location=LocationConfig(country={recipient_location})

STEP 2: Filter and Extract Luma Events
- Filter for events happening in {recipient_location} or nearby areas
- Only include events happening in the next 3 months
- Extract: event name, date (DD/MM/YYYY), time, description, venue, registration URL
- Remove duplicates

STEP 3: Rank and Select Top Luma Events
- Rank events by relevance to "{recipient_interest}" and proximity to {recipient_location}
- Select top 10 most relevant Luma events
- Ensure variety in dates across the 3 months
- Return structured list of top 10 Luma events with all details
"""

print("Running Task 1: Scraping Luma events...")
luma_result = portia.run(
    query=task_luma,
    tools=["portia:mcp:custom:mcp.firecrawl.dev:firecrawl_scrape"]
)

# TASK 2: Scrape Meetup Events
task_meetup = f"""
Please scrape Meetup events for my interest:

USER PROFILE:
- Interest: {recipient_interest}
- Location: {recipient_location}

STEP 1: Scrape Meetup Events
- Use firecrawl to scrape events from: https://www.meetup.com/find/?events=&keywords={recipient_interest}
- Use these firecrawl args: formats=["markdown"], location=LocationConfig(country={recipient_location})

STEP 2: Filter and Extract Meetup Events
- Filter for events happening in {recipient_location}
- Only include events happening in the next 3 months
- Extract: event name, date (DD/MM/YYYY), time, description, venue, registration URL
- Remove duplicates

STEP 3: Rank and Select Top Meetup Events
- Rank events by relevance to "{recipient_interest}" and proximity to {recipient_location}
- Select top 10 most relevant Meetup events
- Ensure variety in dates across the 3 months
- Return structured list of top 10 Meetup events with all details
"""

print("Running Task 2: Scraping Meetup events...")
meetup_result = portia.run(
    query=task_meetup,
    tools=["portia:mcp:custom:mcp.firecrawl.dev:firecrawl_scrape"]
)

# TASK 3: Combine and Email
task_email = f"""
Please combine events and send professional email:

USER PROFILE:
- Interest: {recipient_interest}
- Location: {recipient_location}
- Email: {recipient_email}

LUMA EVENTS DATA:
{luma_result.outputs.final_output.value}

MEETUP EVENTS DATA:
{meetup_result.outputs.final_output.value}

STEP 1: Combine and Final Selection
- Take the top 10 Luma events and top 10 Meetup events (20 events total)
- From these 20 combined events, select the final top 10 most relevant events
- Remove any duplicate events across platforms
- Ensure variety in dates across the 3 months

STEP 2: Create Professional Email
- Recipient: {recipient_email}
- Subject: "Top {recipient_interest} Events in {recipient_location} - Next 3 Months"
- For each of the final top 10 events include:
  * Event name (clear, descriptive)
  * Exact date in DD/MM/YYYY format
  * Time if available (HH:MM format)
  * Detailed description (2-3 sentences)
  * Specific venue/location
  * Direct registration URL
  * Platform source (Meetup/Luma)
- Order events chronologically (earliest first)
- Add context about why events were selected
- Include actionable next steps

STEP 3: Send Email
- Use the email tool to send the formatted email
- Verify all content before sending
- Ensure all URLs are valid and dates are correctly calculated
"""

print("Running Task 3: Combining events and sending email...")
portia.run(query=task_email, tools=["portia:google:gmail:send_email"])

print("All tasks completed!")