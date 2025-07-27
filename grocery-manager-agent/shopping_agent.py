from typing import List
import json
from portia import (
    Portia,
    PlanRunState,
    MultipleChoiceClarification,
    ActionClarification,
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
            4. If the product is not available, search for alternative products. Like for example, if crocin is not available, search for paracetamol.
            5. Extract the search results in format:
               {{
                   "results": [
                       {{
                           "name": "Product Name",
                           "price": "£X.XX"
                       }}
                   ],
                   "alternative": "true if these are alternative products for {item}, false if exact matches"
               }}
            6. Call the alternatives tool with the search results.
            7. Add the chosen product to cart (unless skipped).
            """

        plan_run = self.portia.run(task)

        while plan_run.state == PlanRunState.NEED_CLARIFICATION:
            for clarification in plan_run.get_outstanding_clarifications():
                if isinstance(clarification, MultipleChoiceClarification):
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
                elif isinstance(clarification, ActionClarification):
                    print(f"\n🔐 {clarification.user_guidance}")
                    print("Please complete the action and press Enter to continue...")
                    input()
                    plan_run = self.portia.resolve_clarification(
                        clarification, "completed", plan_run
                    )

            plan_run = self.portia.resume(plan_run)

        # Check if the item was skipped
        try:
            result = json.loads(plan_run.model_dump_json())
            if (
                "outputs" in result
                and "step_outputs" in result["outputs"]
                and "$alternatives" in result["outputs"]["step_outputs"]
            ):
                alternatives_output = json.loads(
                    result["outputs"]["step_outputs"]["$alternatives"]["value"]
                )
                if alternatives_output.get("product") == "":
                    print(f"⏭️ Skipped {item}")
                    return

        except (json.JSONDecodeError, KeyError, AttributeError):
            pass  # If we can't parse the output, assume it wasn't skipped

        print(f"✅ Completed adding {item}")
        print(plan_run.model_dump_json(indent=2))

    def process_list(self) -> None:
        """Process a list of grocery items."""
        for item in self.grocery_list:
            self.process_item(item)

    def notify_user(self):
        task = f"""Get cart summary from {self.grocery_website} and notify user of the details and to checkout"""
        self.portia.run(task)
