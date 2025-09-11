from events_discover import EventDiscoveryAgent
from event_registration import EventRegistrationAgent
from email_service import EmailService
import json
import argparse

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as file:
        return json.load(file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default='data.json',
                       help='Path to configuration JSON file')
    args = parser.parse_args()
    
    config = load_config(args.config)

    # Discover events
    discovery_agent = EventDiscoveryAgent()
    #registration event
    event_registration = EventRegistrationAgent()
    # emailservice agent
    email_sent = EmailService()
    
    if config['automatic_registration'] == "Yes":
        events = discovery_agent.run(config, has_form= False)
        events_attendance = event_registration.run(config, events)
        email_sent.run(events_attendance, config)
    else:
        events = discovery_agent.run(config, has_form = True)
        email_sent.run(events, config)
        
if __name__ == "__main__":
    main()