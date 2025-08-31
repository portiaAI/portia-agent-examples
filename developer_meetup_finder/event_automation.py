from dotenv import load_dotenv
from portia.cli import CLIExecutionHooks
from portia import Portia, Config, ToolRegistry, default_config, DefaultToolRegistry
from portia.open_source_tools.browser_tool import (BrowserTool, BrowserInfrastructureOption)

load_dotenv(override=True)

browser_tool = BrowserTool(infrastructure_option=BrowserInfrastructureOption.REMOTE)

default_registry = DefaultToolRegistry(default_config())
tool_registry = ToolRegistry([browser_tool])
all_tools = default_registry + tool_registry

portia = Portia(
    config=Config.from_default(),
    execution_hooks=CLIExecutionHooks(),
    tools=all_tools)

class EventRegistrationAgent:
    def __init__(self, portia: Portia, event_url: str, user_data: dict):
        self.portia = portia
        self.event_url = event_url
        self.user_data = user_data

    def register(self, end_user: str | None = None):
        task = f"""
        1. Navigate to {self.event_url}
        2. Fill out registration form with: {self.user_data}
        3. Submit the registration
        4. Confirm successful registration
        """
        return self.portia.run(task, end_user=end_user)

selected_event_url = ""

registration_agent = EventRegistrationAgent(
    portia=portia,
    event_url=selected_event_url,
    user_data={
        "name": "",
        "email": "",
    },)

registration_result = registration_agent.register(end_user="")
