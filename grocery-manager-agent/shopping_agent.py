from typing import List
from portia import (
    Portia,
)


class ShoppingAgent:
    """Agent responsible for managing grocery shopping tasks."""

    def __init__(self, portia: Portia, grocery_website: str, grocery_list: List[str]):
        """Initialize shopping agent with Portia instance and grocery website."""
        self.portia = portia
        self.grocery_website = grocery_website
        self.grocery_list = grocery_list

    def process_item(self, item: str) -> None:
        """Process a single grocery item."""
        print(f"\n🛒 Processing item: {item}")
        task = f"""
            For the item "{item}":
            1. Navigate to grocery store website ({self.grocery_website}).
            2. Make sure user is logged in.
            3. Search for it on grocery store website ({self.grocery_website}).
            4. If the product is not available, search for alternative products. Like for example, if crocin is not available, search for paracetamol and add search results for the alternative product.
            5. Extract the search results in format:
               {{
                   "grocery_items": [
                       {{
                           "name": "Product Name",
                           "price": "£X.XX"
                       }}
                   ],
                   "alternative": "true if these are alternative products for {item}, false if exact matches",
                   "original_search_query": "{item}"
               }}
            6. Call the alternatives tool with the search results.
            7. Add the chosen product to cart (unless skipped).
            """

        plan_run = self.portia.run(task)

        print(f"✅ Completed adding {item}")
        print(plan_run.model_dump_json(indent=2))

    def process_list(self) -> None:
        """Process a list of grocery items."""
        for item in self.grocery_list:
            self.process_item(item)

    def notify_user(self):
        task = f"""Get cart summary from {self.grocery_website} and notify user of the details and to checkout"""
        self.portia.run(task)
