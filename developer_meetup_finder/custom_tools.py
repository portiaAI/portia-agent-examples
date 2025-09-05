import os, requests
import pandas as pd
from portia import tool
from typeform import Typeform
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from firecrawl import Firecrawl
from typing import List, Dict, Any, Optional

load_dotenv()

app = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])
tf = Typeform(token=os.environ["TYPEFORM_API_TOKEN"])

class EventSchema(BaseModel):
    event_name: str = Field(..., description="The name/title of the event")
    event_date: str = Field(..., description="Date in ISO format YYYY-MM-DD")
    event_time: Optional[str] = Field(None, description="Time, ideally HH:MM in 24-hour format")
    event_location: Optional[str] = Field(None, description="Location name or city")
    event_url: str = Field(..., description="Canonical URL for the event")
    
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
        "prompt": "Look for the events most relevant and extract their names, dates, times, locations, and the registration URL."}],
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


def download_typeform_as_csv(form_id: str, api_token: str, filename: str = "responses.csv") -> str:
    """Download Typeform responses as CSV file."""
    
    # Get responses from Typeform API
    response = requests.get(
        f"https://api.typeform.com/forms/{form_id}/responses",
        headers={"Authorization": f"Bearer {api_token}"},
        params={"page_size": 1000}
    )
    response.raise_for_status()
    
    data = response.json()["items"]
    if not data:
        return None
    
    # Flatten responses to DataFrame
    rows = []
    for item in data:
        row = {
            "response_id": item["response_id"],
            "submitted_at": item["submitted_at"],
        }
        
        # Add answer data
        for answer in item.get("answers", []):
            field_title = answer["field"]["ref"] or answer["field"]["id"]
            
            if "text" in answer:
                row[field_title] = answer["text"]
            elif "choice" in answer:
                row[field_title] = answer["choice"]["label"]
            elif "choices" in answer:
                row[field_title] = "; ".join([c["label"] for c in answer["choices"]])
            elif "boolean" in answer:
                row[field_title] = answer["boolean"]
            elif "number" in answer:
                row[field_title] = answer["number"]
            elif "email" in answer:
                row[field_title] = answer["email"]
            elif "date" in answer:
                row[field_title] = answer["date"]
            elif "file_url" in answer:
                row[field_title] = answer["file_url"]
        
        rows.append(row)
    
    # Save as CSV
    pd.DataFrame(rows).to_csv(filename, index=False)
    return filename