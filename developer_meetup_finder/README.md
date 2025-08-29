# Portia Developer Meetup Finder

This agent discovers and curates relevant tech events and meetups from Luma and Meetup based on user interests and location. It scrapes events using Firecrawl, filters them for relevance and proximity, and sends personalized event recommendations via Gmail. The agent can handle multiple interests and provides intelligent event curation across a 3-month timeframe.

## Introduction

This example demonstrates how to build an intelligent meetup discovery system using the Portia SDK with custom web scraping tools. The agent combines data from multiple event platforms (Luma and Meetup) to create personalized developer event recommendations. It showcases custom tool creation, web scraping with structured data extraction, and automated Gmail communication.

The agent reads user preferences from a JSON configuration file, discovers events across multiple categories and platforms, applies intelligent filtering and ranking, and delivers curated recommendations via professional HTML email using Gmail integration.

You can read more about building custom tools in the [Portia SDK documentation](https://docs.portialabs.ai/add-custom-tools).

## Prerequisites

Before running this agent, you'll need the following:

- Python 3.11 (or greater): You can download it from [python.org](https://www.python.org/downloads/) or install it using [pyenv](https://github.com/pyenv/pyenv)
- UV: We use uv to manage dependencies. You can install it from [here](https://docs.astral.sh/uv/concepts/projects/dependencies/).
- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai) > API Keys.
- An OpenAI API key: You can get one from [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
- A Firecrawl API key: You can get one from [firecrawl.dev](https://firecrawl.dev)

## Setup

1. Clone the repository and navigate to this folder.
2. Install the required Python packages:
   ```bash
   pip install firecrawl-py portia python-dotenv pydantic
   ```
3. Copy the `.env.example` file to `.env` and add your API keys:
   ```
   PORTIA_API_KEY=your_portia_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   ```
4. Configure your `data.json` file with your event discovery preferences:
   ```json
   {
     "recipient_interest": [],
     "recipient_location": "",
     "recipient_email": "",
     "recipient_name": "",
     "no_of_events": 
   }
   ```

## Usage

Run the meetup finder:

```bash
python main.py
```

The agent will:
1. Discover events from Luma across relevant categories (AI, Arts & Culture, Climate, Fitness, Wellness, Crypto)
2. Search Meetup for events matching your interests
3. Filter and rank events by relevance, proximity, and temporal distribution
4. Send a curated list of events via email

## Understanding the code

### Custom Tool Integration

The agent defines custom tools in `custom_tools.py` for scraping event data:

- `luma_events`: Scrapes events from Luma category pages using structured data extraction
- `meetup_events`: Searches and extracts events from Meetup based on keyword queries

Both tools use Firecrawl's JSON extraction capabilities with Pydantic schemas to ensure consistent data structure.

### Multi-Platform Event Discovery

The agent implements a sophisticated discovery pipeline:

1. **Interest Analysis**: Parses multiple interests and maps them to relevant Luma categories
2. **Platform Integration**: Simultaneously queries both Luma and Meetup platforms
3. **Intelligent Filtering**: Removes duplicates, filters by location/timeframe, and ranks by relevance
4. **Temporal Distribution**: Ensures event recommendations are spread across the 3-month window

### Structured Data Extraction

Using Pydantic schemas, the agent extracts:
- Event name and description
- Date and time information
- Location details
- Registration URLs
- Platform source

### Gmail Integration

The final step generates professional HTML emails using Portia's Gmail tool integration with:
- Chronologically ordered event listings
- Platform-specific registration buttons ("Register on Luma" / "Register on Meetup")
- Consistent formatting and branding
- Personalized content based on user interests and location

## Configuration

### Supported Interest Categories

**Luma Categories:**
- AI → https://lu.ma/ai
- Arts & Culture → https://lu.ma/arts  
- Climate → https://lu.ma/climate
- Fitness → https://lu.ma/fitness
- Wellness → https://lu.ma/wellness
- Crypto → https://lu.ma/crypto

**Meetup:** Supports any keyword-based search with automatic URL encoding

### Location Processing

The agent processes city names and converts them to ISO 3166-1 alpha-2 country codes for accurate regional filtering. Simply provide your city name (e.g., "London", "New York", "Berlin").

### Data Format

The `data.json` configuration supports:
- **recipient_name**: Full name for email personalization
- **recipient_email**: Target email address  
- **recipient_location**: City name (e.g., "London", "San Francisco")
- **recipient_interest**: Array of interests (e.g., ["AI", "machine learning", "blockchain"])
- **no_of_events**: Number of events to include in final recommendations (integer)
