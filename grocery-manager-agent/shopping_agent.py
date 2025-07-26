from typing import List
from portia import Portia, PlanRunState


class ShoppingAgent:
    """Agent responsible for managing grocery shopping tasks."""

    def __init__(self, portia: Portia, grocery_website: str):
        """Initialize shopping agent with Portia instance and grocery website."""
        self.portia = portia
        self.grocery_website = grocery_website

    def process_item(self, item: str) -> None:
        """Process a single grocery item."""
        print(f"\n🛒 Processing item: {item}")
        task = f"""
            For the item "{item}":
            1. Search for it on Morrisons website ({self.grocery_website}).
            2. If the product is not available, search for alternative relevant products. Like for crocin, search for paracetamol.
            3. Extract the search results in format:
               {{
                   "results": [
                       {{
                           "name": "Product Name",
                           "price": "£X.XX"
                       }}
                   ],
                   "alternative": "true if these are alternative products for {item}, false if exact matches"
               }}
            4. Call the alternatives tool with the search results.
            5. Add the chosen product to cart
            6. Stop after adding this item
            """

        plan_run = self.portia.run(task)

        while plan_run.state == PlanRunState.NEED_CLARIFICATION:
            for clarification in plan_run.get_outstanding_clarifications():
                print(f"\n🤔 {clarification.user_guidance}")
                print("\nOptions:")
                for i, option in enumerate(clarification.options, 1):
                    print(f"{i}. {option}")

                while True:
                    user_input = input("\nPlease choose (enter number): ")
                    try:
                        choice = int(user_input)
                        if 1 <= choice <= len(clarification.options):
                            selected = clarification.options[choice - 1]
                            plan_run = self.portia.resolve_clarification(
                                clarification, selected, plan_run
                            )
                            break
                    except ValueError:
                        pass
                    print("Invalid selection. Please try again.")

            plan_run = self.portia.resume(plan_run)

        print(f"✅ Completed adding {item}")
        print(plan_run.model_dump_json(indent=2))

    def process_list(self, grocery_list: List[str]) -> None:
        """Process a list of grocery items."""
        if not grocery_list:
            print("⚠️ No grocery list provided")
            return
        for item in grocery_list:
            self.process_item(item)
