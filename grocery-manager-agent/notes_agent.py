from typing import List
import json
from portia import Portia
from portia import (
    PlanRunState,
    ActionClarification,
)


class NotesAgent:
    """Agent responsible for extracting grocery lists from notes apps."""

    def __init__(self, portia: Portia, notes_website: str):
        """Initialize notes agent with Portia instance and notes website."""
        self.portia = portia
        self.notes_website = notes_website

    def get_grocery_list(self) -> List[str]:
        """Get grocery list from notes app.

        Returns:
            List[str]: List of grocery items
        """
        task = f"""
            Navigate to {self.notes_website} and search for and extract my grocery list from the specified note.
            Login if necessary.
            Extract the grocery list in format:
            {{
                "grocery_list": ["item1", "item2", "item3"]
            }}
            Return ONLY the JSON object, no additional text.
        """
        plan_run = self.portia.run(task)

        while plan_run.state == PlanRunState.NEED_CLARIFICATION:
            for clarification in plan_run.get_outstanding_clarifications():
                if isinstance(clarification, ActionClarification):
                    print(f"\n🔐 {clarification.user_guidance}")
                    print("Please complete the action and press Enter to continue...")
                    input()
                    plan_run = self.portia.resolve_clarification(
                        clarification, "completed", plan_run
                    )
            plan_run = self.portia.resume(plan_run)

        final_output = json.loads(plan_run.outputs.final_output.value)
        if "grocery_list" not in final_output:
            print("⚠️ Grocery list not found in final output")
            return []
        return final_output["grocery_list"]
