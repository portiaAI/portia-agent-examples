from typing import Tuple
from portia import (
    Portia,
    Config,
    ToolRegistry,
)
from portia.open_source_tools.browser_tool import (
    BrowserTool,
    BrowserInfrastructureOption,
)
from grocery_tool import GroceryAlternativesTool
from shopping_agent import ShoppingAgent
from notes_agent import NotesAgent
from portia.cli import CLIExecutionHooks


# This method can be extended to support other notes apps and grocery stores.
def get_user_preferences() -> Tuple[str, str]:
    """Get user preferences for notes app and grocery store.

    Returns:
        Tuple[str, str]: Tuple of (grocery_website, notes_website)
    """
    print("👋 Hi! I'm your grocery shopping assistant.")
    print(
        "Currently, Google Keep is the supported notes app and Morrisons is the supported grocery store."
    )
    print("Let's start shopping! 🛒\n")

    notes_website = "https://keep.google.com/"
    grocery_website = "https://groceries.morrisons.com"

    return grocery_website, notes_website


if __name__ == "__main__":
    browser_tool = BrowserTool(infrastructure_option=BrowserInfrastructureOption.LOCAL)
    alternatives_tool = GroceryAlternativesTool()

    tool_registry = ToolRegistry([browser_tool, alternatives_tool])
    portia = Portia(
        config=Config.from_default(),
        execution_hooks=CLIExecutionHooks(),
        tools=tool_registry,
    )

    grocery_website, notes_website = get_user_preferences()

    # Create the notes agent and get the grocery list
    print(f"📝 Getting grocery list from {notes_website}")
    notes_agent = NotesAgent(portia, notes_website)
    grocery_list = notes_agent.get_grocery_list()

    print(f"📝 Found grocery list: {grocery_list}")
    print(grocery_list)

    # Create and use the shopping agent
    print(f"🛒 Shopping at {grocery_website}")
    agent = ShoppingAgent(portia, grocery_website, grocery_list)
    agent.process_list()
    agent.notify_user()
