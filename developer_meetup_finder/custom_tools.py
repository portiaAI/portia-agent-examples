import os
from portia import tool
from typeform import Typeform
from pydantic import BaseModel
from dotenv import load_dotenv
from firecrawl import Firecrawl
from datetime import date, time
from typing import List, Dict, Any

load_dotenv()

app = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])
tf = Typeform(token=os.environ["TYPEFORM_API_TOKEN"])

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

@tool
def create_typeform(title: str, form_description: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a Typeform with event selection questions.
    
    Args:
        title: Form title
        description: Form description 
        events: List of event dictionaries with keys: event_name, event_date, event_time, event_location, event_url
    
    Returns:
        Dict with form_url, form_id, and workspace_id
    """
    fields = [
        {
            "title": "What's your name?",
            "type": "short_text",
            "properties": {"description": "Please enter your full name"},
            "validations": {"required": True}
        },
    ]
   
    for event in events:
        event_title = f"Are you interested in: {event['event_name']}?"
        event_description = f"📅 {event['event_date']} at {event['event_time']}\n📍 {event['event_location']}\n🔗 {event['event_url']}"
        
        field = {
            "title": event_title,
            "type": "multiple_choice",
            "properties": {
                "description": event_description,
                "choices": [
                    {"label": "Yes, I'm interested"},
                    {"label": "No, not interested"}
                ]
            },
            "validations": {"required": True}
        }
        fields.append(field)
    
    # Create the form
    form_data = {
        "title": title,
        "settings": {
            "is_public": True,
            "progress_bar": "proportion",
            "show_progress_bar": True,
            "show_typeform_branding": True
        },
        "theme": {"href": "https://api.typeform.com/themes/6lPNE6"},
        "fields": fields,
        "welcome_screens": [{
            "title": title,
            "properties": {"description": form_description, "show_button": True, "button_text": "Start"}
        }],
        "thankyou_screens": [{
            "title": "Thank you!",
            "properties": {"description": "We'll be in touch about the events you're interested in.", "show_button": False}
        }]
    }
    
    # Create form using Typeform API
    response = tf.forms.create(form_data)
    
    return response["_links"]["display"]