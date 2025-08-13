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

task = f"""
Please help me discover and email the best events across multiple platforms:

USER PROFILE:
- Interest: {recipient_interest}
- Location: {recipient_location}
- Email: {recipient_email}

STEP 1: Scrape Luma Events
- Classify the user interest "{recipient_interest}" into ONE of these Luma categories: AI, Arts & Culture, Climate, Fitness, Wellness, Crypto
- Use the appropriate category URL from: https://lu.ma/ai, https://lu.ma/arts, https://lu.ma/climate, https://lu.ma/fitness, https://lu.ma/wellness, https://lu.ma/crypto
- Use firecrawl with: formats=["markdown"], location=LocationConfig(country={recipient_location})
- Filter for events happening in {recipient_location} or nearby areas
- Only include events happening in the next 3 months
- Extract: event name, date (DD/MM/YYYY), time, description, venue, registration URL
- Remove duplicates
- Rank events by relevance to "{recipient_interest}" and proximity to {recipient_location}
- Select top 10 most relevant Luma events

STEP 2: Scrape Meetup Events
- Use firecrawl to scrape events from: https://www.meetup.com/find/?events=&keywords={recipient_interest}
- Use these firecrawl args: formats=["markdown"], location=LocationConfig(country={recipient_location})
- Filter for events happening in {recipient_location}
- Only include events happening in the next 3 months
- Extract: event name, date (DD/MM/YYYY), time, description, venue, registration URL
- Remove duplicates
- Rank events by relevance to "{recipient_interest}" and proximity to {recipient_location}
- Select top 10 most relevant Meetup events

STEP 3: Combine and Final Selection
- Take the top 10 Luma events and top 10 Meetup events (20 events total)
- From these 20 combined events, select the final top 10 most relevant events
- Rank by relevance to "{recipient_interest}" and proximity to {recipient_location}
- Remove any duplicate events across platforms
- Ensure variety in dates across the 3 months

STEP 4: Create Professional Email
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

STEP 5: Send Email
- Use the email tool to send the formatted email
- Verify all content before sending
- Ensure all URLs are valid and dates are correctly calculated

IMPORTANT: Structure your internal data processing using this JSON format for consistency:
{{
  "events": [
    {{
      "name": "Event Title Here",
      "date": "DD/MM/YYYY",
      "time": "HH:MM",
      "description": "Detailed description here",
      "venue": "Specific venue/location",
      "registration_url": "Direct URL",
      "platform": "Meetup" or "Luma"
    }}
  ]
}}
"""

config = Config.from_default()
portia = Portia(config=config,
    tools=DefaultToolRegistry(config=config),
    execution_hooks=CLIExecutionHooks(),)

portia.run(
    query=task,
    tools=["portia:mcp:custom:mcp.firecrawl.dev:firecrawl_scrape", "portia:google:gmail:send_email"]
)