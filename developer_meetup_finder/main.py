from events_discover import EventDiscoveryAgent
from event_registration import EventRegistrationAgent
from email_service import EmailService
import json, argparse

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
    discovery_agent = EventDiscoveryAgent(
        recipient_interest=config['recipient_interest'],
        recipient_location=config['recipient_location'],
        no_of_events=config['no_of_events'],
        recipient_name=config['recipient_name'],
        has_form = True if config['automatic_registration'] == "Yes" else False)
    # Register for events
    event_registration = EventRegistrationAgent(config)
    email_sent = EmailService(config)
    
    if config['automatic_registration'] == "Yes":
        events = discovery_agent.run()
        events_attendance = event_registration.run(events)
        email_sent.run(events_attendance)
    else:
        events = discovery_agent.run()
        email_sent.run(events)
        
if __name__ == "__main__":
    main()
    
