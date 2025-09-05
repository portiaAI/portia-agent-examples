# Portia Developer Meetup Finder

This agent discovers and curates relevant tech events and meetups from Luma and Meetup based on user interests and location. It automatically registers users for events using browser automation or creates dynamic RSVP forms via Typeform, and sends intelligent email notifications with registration status updates. The system provides end-to-end event management across a 3-month timeframe.

## Introduction

This example demonstrates how to build an intelligent, fully-automated meetup discovery and registration system using the Portia SDK. The agent combines data from multiple event platforms (Luma and Meetup), automatically registers users for events using browser automation, and provides intelligent email communication with context-aware content.

The system features a modular architecture with three specialized agents:
- **Event Discovery Agent**: Scrapes and curates events from multiple platforms
- **Event Registration Agent**: Automatically registers users using browser automation
- **Email Service**: Sends context-aware notifications with registration updates

You can read more about building custom tools in the [Portia SDK documentation](https://docs.portialabs.ai/add-custom-tools) and browser automation in the [Browser Tool documentation](https://docs.portialabs.ai/browser-tools).

## Prerequisites

Before running this agent, you'll need the following:

- Python 3.12.5 (or greater): You can download it from [python.org](https://www.python.org/downloads/) or install it using [pyenv](https://github.com/pyenv/pyenv)
- UV: We use uv to manage dependencies. You can install it from [here](https://docs.astral.sh/uv/concepts/projects/dependencies/).
- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai).
- An OpenAI API key: You can get one from [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
- A Firecrawl API key: You can get one from [firecrawl.dev](https://firecrawl.dev)
- A Typeform API token: You can get one from [developer.typeform.com](https://developer.typeform.com/get-started/personal-access-token/)
- Gmail configured in your Portia tool registry: You can enable it by going to the [Portia tool registry](https://app.portialabs.ai/dashboard/tool-registry) in the dashboard and configure Gmail for sending emails.

## Setup

1. Clone the repository and navigate to this folder.
2. Install dependencies using uv:
   ```
   bashuv sync
   ```
3. Copy the `.env.example` file to `.env` and add your API keys:
   ```
   PORTIA_API_KEY=your_portia_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   TYPEFORM_API_TOKEN=your_typeform_api_key_here
   ```
4. Configure your `data.json` file with your event discovery preferences:
   ```json
   {
   "recipient_interest": [],
   "recipient_location": "",
   "recipient_email": "",
   "recipient_name": "",
   "no_of_events": 0,
   "Job Title":"",
   "Company":"",
   "Linkedin":"",
   "Automatic_registration": "Yes"
   }
   ```

## Usage

### Basic Event Discovery and Registration

Run the complete meetup finder with automatic registration:

```bash
python main.py
```

### Event Discovery Only (No Registration)

Run without automatic registration:

```bash
python main.py --config data.json
```

### Command Line Options

- `--config`, `-c`: Path to configuration JSON file (default: `data.json`)

## Features

The agent will:
1. **Discover Events**: Search Luma and Meetup for events matching your interests and location
2. **Intelligent Filtering**: Remove duplicates, rank by relevance and proximity
3. **Automatic Registration**: Use browser automation to register for events (skips paid events)
4. **Form Creation**: Generate Typeform for RSVP collection when needed
5. **Smart Email Notifications**: Send context-aware emails with registration status updates

## Understanding the Architecture

### Modular Agent System

The system is built with three specialized agents:

#### 1. Event Discovery Agent (`events_discover.py`)
- Scrapes events from Luma category pages and Meetup search results
- Uses Firecrawl for structured data extraction with Pydantic schemas
- Implements intelligent filtering and deduplication across platforms
- Optionally creates Typeform for RSVP collection

#### 2. Event Registration Agent (`event_registration.py`)
- Uses Portia's Browser Tool for automated event registration
- Handles form filling with user configuration data
- Manages different registration scenarios (free events, waitlists, group joins)
- Returns detailed registration status for each event

#### 3. Email Service (`email_service.py`)
- Context-aware email generation based on registration outcomes
- Adaptive content strategy (discovery-only vs. registration updates)
- Professional HTML formatting with chronological event ordering
- Integration with Gmail via Portia's email tools

### Custom Tool Integration

The system defines several custom tools in `custom_tools.py`:

- **`luma_events`**: Scrapes events from Luma category pages using structured JSON extraction
- **`meetup_events`**: Searches Meetup with keyword-based queries and location filtering
- **`create_typeform`**: Dynamically generates forms with event-specific RSVP questions

### Automated Browser Registration

The registration agent uses sophisticated browser automation:

```python
# Registration rules implemented:
- Prefer 'In person' events over virtual
- Skip events requiring payment
- Auto-join groups when prompted
- Fill forms using configuration data
- Handle subscription prompts intelligently
- Capture registration status and feedback
```

### Intelligent Email Adaptation

The email service adapts content based on context:

**Registration Mode**: Includes registration status, success/failure details, and event links
**Discovery Mode**: Focuses on event showcase with optional Typeform integration

## Configuration

### Registration Configuration

The `data.json` file should include personal details for form filling:

- **recipient_name**: Full name for registration forms
- **recipient_email**: Email for event registration and notifications
- **recipient_location**: City name for location-based filtering
- **recipient_interest**: Array of interests for event discovery
- **no_of_events**: Maximum number of events to process
- **Job Title**: Professional title for networking forms
- **Company**: Company name for professional event registration
- **Linkedin**: LinkedIn profile URL for networking opportunities
- **Automatic_registration**: "Yes" or "No" to enable/disable auto-registration

### Browser Automation Settings

The system uses local browser infrastructure by default. Registration behavior:
- **Free events**: Attempts registration automatically
- **Paid events**: Skips registration, includes in email for manual review
- **Group membership**: Automatically joins when required
- **Form fields**: Uses configuration data with reasonable fallbacks
- **Retry logic**: Attempts registration twice per event before marking as failed

## Send Emails Monthly (cron)

You can schedule this example to **send emails once a month** on your machine using **cron** (macOS/Linux). This keeps everything local—no GitHub Actions required.

> Cron runs in your machine’s **local time**.

### 1) Find your Python interpreter (absolute path)

Use a full path to avoid cron PATH issues.

```bash

python -c 'import sys; print(sys.executable)'

```

Copy the printed path.

### 2) Choose a log location

Avoid Desktop/Documents because macOS privacy can block cron. Use:

```bash

mkdir -p log_location

```

### 3) Setup Cron for your usecase

Edit your crontab:

```bash 
crontab -e
```

Paste this in the cron tab, runs on a monthly schedule (09:00 on 1st of every month):

```

0 9 1 * * cd /absolute/path/to/your/project && /absolute/path/to/python main.py >> log_location/monthly.log 2>&1

```
