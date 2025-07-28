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


def get_user_preferences() -> Tuple[str, str]:
    """Get user preferences for notes app and grocery store.

    Returns:
        Tuple[str, str]: Tuple of (grocery_website, notes_website)
    """
    print("👋 Hi! I'm your grocery shopping assistant.")
    print("Let me ask you a couple of quick questions...\n")

    print("Which notes app do you use for your grocery lists?")
    print("(Google Keep is supported as of now, others coming soon!)")
    notes_app = input("Your notes app: ").strip()

    print("Which grocery store would you like to shop at?")
    print("(Morrisons is supported as of now, others coming soon!)")
    grocery_store = input("Your preferred store: ").strip()

    notes_app_lower = notes_app.lower()
    store_lower = grocery_store.lower()

    if any(word in notes_app_lower for word in ["keep", "google", "gogle", "kep"]):
        notes_website = "https://keep.google.com/"
    else:
        # default to google keep
        notes_website = "https://keep.google.com/"

    if any(word in store_lower for word in ["morrison", "morisons", "morrisson"]):
        grocery_website = "https://groceries.morrisons.com"
    else:
        # default to morrisons
        grocery_website = "https://groceries.morrisons.com"

    print("Let's start shopping! 🛒\n")

    return grocery_website, notes_website


if __name__ == "__main__":
    browser_tool = BrowserTool(infrastructure_option=BrowserInfrastructureOption.LOCAL)
    alternatives_tool = GroceryAlternativesTool()

    tool_registry = ToolRegistry([browser_tool, alternatives_tool])
    portia = Portia(config=Config.from_default(), tools=tool_registry)

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
