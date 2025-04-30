# type: ignore
# ruff: noqa

import os
from pathlib import Path
import re

from dotenv import load_dotenv

from portia import Portia, PortiaToolRegistry, Config, StorageClass
from portia.open_source_tools.browser_tool import BrowserToolForUrl, BrowserInfrastructureOption
from portia.cli import CLIExecutionHooks

load_dotenv(override=True)

print("To run this agent, you need to have a Google account and 2 Google docs:")
print("1. Outreach messages doc: This should contain any messages that you want the agent to parse "
      "and create connections for the LinkedIn profiles within it.")
print("2. Outreach criteria doc: This should contain the criteria that the agent will use to assess "
      "the LinkedIn profiles.")
print("The document ID of the Google docs can be found in the URL of the document after the "
      "'document/d/' part.")
outreach_messages_doc_id = input("Please enter the ID of the outreach messages doc: ")
outreach_criteria_doc_id = input("Please enter the ID of the outreach criteria doc: ")

my_config = Config.from_default(storage_class=StorageClass.CLOUD)
portia = Portia(
    config=my_config,
    tools=(
        PortiaToolRegistry(my_config) +
        [BrowserToolForUrl("https://www.linkedin.com",
                           # You can also use BrowserInfrastructureOption.REMOTE and use Browserbase
                           infrastructure_option=BrowserInfrastructureOption.LOCAL)]
    ),
    execution_hooks=CLIExecutionHooks(),
)

def read_task_from_file(filepath: str) -> str:
    try:
        with open(f'./{filepath}', 'r') as file:
            return file.read().strip()
    except FileNotFoundError as e:
        print(f"Error: {filepath} not found!")
        raise e

plan_run = portia.run(
    query=read_task_from_file("retrieve_potential_connections.txt").replace(
        "{outreach_messages_id}", outreach_messages_doc_id
    ),
    tools=["portia:google:docs:get_document"],
    )

def extract_linkedin_urls(text: str) -> list[str]:
    """Extract LinkedIn URLs from the given text.
    
    Args:
        text (str): Text containing LinkedIn URLs
        
    Returns:
        list[str]: List of extracted LinkedIn URLs
    """
    pattern = r'(?:https?://)?\w*?\.?linkedin\.com/in/[a-zA-Z0-9_-]+/?'
    return re.findall(pattern, text)

# After getting the output, extract the URLs
linkedin_urls = extract_linkedin_urls(plan_run.outputs.final_output.value)

for url in linkedin_urls:
    plan_run = portia.run(read_task_from_file("research_and_connect.txt").replace(
        "{linked_in_profile_url}", url).replace(
            "{outreach_criteria_id}", outreach_criteria_doc_id))
    output = plan_run.outputs.final_output.value
    print(plan_run.model_dump_json(indent=2))