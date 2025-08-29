import os
from portia import tool
from dotenv import load_dotenv
from pydantic import BaseModel
from firecrawl import Firecrawl
from datetime import date, time
from typing import List, Dict, Any

load_dotenv()

app = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])

class EventSchema(BaseModel):
    event_name: str
    event_date: date
    event_time: time
    event_location: str
    event_url: str
    
class EventsSchema(BaseModel):
    events: List[EventSchema]
    
@tool
def luma_events(url, location) -> Dict[str, Any]:
  result = app.scrape(url,
      formats=[{
        "type": "json",
        "schema": EventsSchema,
        "prompt": "Look for the 'Nearby Events' section and extract all events listed there with their names, dates, times, locations, and the registration URL."
      }],
      location={
        'country': location,
      },
      only_main_content=False,
      timeout=120000,
      wait_for=5000)
  return result.json

@tool
def meetup_events(url, location) -> Dict[str, Any]:
    result = app.scrape(url,
        formats=[{
        "type": "json",
        "schema": EventsSchema,
        "prompt": "Look for the most events most relevant and extract their names, dates, times, locations, and the registration URL."}],
        location={
        'country': location,
        },
        only_main_content=False,
        timeout=120000,
        wait_for=7500)
    return result.json
