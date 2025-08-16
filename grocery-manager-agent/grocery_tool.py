from typing import Dict
import json
from pydantic import BaseModel, Field
from portia import Tool, ToolRunContext, MultipleChoiceClarification


class GroceryAlternativesToolSchema(BaseModel):
    """Schema defining the inputs for the GroceryAlternativesTool.

    This schema expects a JSON string containing grocery items and their prices,
    along with a flag indicating if these are alternative products. It also handles
    the user's choice when selecting from multiple options."""

    options: str = Field(
        ...,
        description="JSON string containing grocery items with their names and prices in format: {'grocery_items': [...], 'alternative': bool}",
    )
    choice: str | None = Field(
        None, description="User's choice from the presented alternatives"
    )


class GroceryAlternativesTool(Tool[Dict[str, str]]):
    """A tool for handling grocery product alternatives and user choices.
    The tool expects grocery items in a specific JSON format:
    {
        "grocery_items": [
            {
                "name": "Product Name",
                "price": "£X.XX"
            }
        ],
        "alternative": true/false  # Indicates if these are alternative products,
        "original_search_query": Product # The original search query that was used to find the alternatives
    }
    If alternative is false, then the tool will return the first product in the list.
    If alternative is true, then the tool will return a MultipleChoiceClarification for user input
    allowing the user to choose from the available products or skip the item.
    """

    id: str = "alternatives"
    name: str = "Product Alternatives Tool"
    description: str = "Used to display alternatives to the human user and retrieve their preferred choice."
    args_schema: type[BaseModel] = GroceryAlternativesToolSchema
    output_schema: tuple[str, str] = (
        json.dumps(
            {
                "type": "object",
                "properties": {"product": {"type": "string"}},
                "required": ["product"],
            }
        ),
        "Returns chosen product",
    )

    def run(
        self, ctx: ToolRunContext, options: str, choice: str | None = None
    ) -> Dict[str, str] | MultipleChoiceClarification:
        """Handle product alternatives through user clarification.

        Args:
            ctx: The tool run context from Portia
            options: JSON string containing available grocery items and alternatives flag
            choice: Optional user's selection from previous clarification

        Returns:
            If choice is provided: Dict with chosen product name or empty string if skipped
            If no choice: MultipleChoiceClarification to get user's selection"""

        if choice:
            if choice == "Skip this item":
                print("⏭️ Skipping this item")
                return {"product": ""}
            print(f"User chose: {choice}")
            return {"product": choice.split(" - ")[0]}

        print(f"🔍 Processing options: {options}")

        try:
            data = json.loads(options)
            products = data["grocery_items"]
            alternative = data["alternative"]
            print(f"🔍 Alternative: {alternative}")
            if not alternative:
                print("🔍 Product is available")
                return {"product": products[0]["name"]}
            print(f"🔍 Parsed products: {products}")
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"Failed to parse grocery items: {e}")
            return {"product": ""}

        options = []
        print(f"🔍 Products: {products}")
        for product in products[:5]:
            name = product.get("name", "")
            price = product.get("price", "")
            print(f"🔍 Product: {name} - {price}")
            if name and price:
                options.append(f"{name} - {price}")
        print(f"🔍 Options: {options}")

        if not options:
            print("No valid options found")
            return {"product": ""}

        options.append("Skip this item")

        user_guidance = (
            f"Choose an alternative for '{data['original_search_query']}' (or skip):"
        )
        clarification = MultipleChoiceClarification(
            user_guidance=user_guidance,
            options=options,
            argument_name="choice",
            plan_run_id=str(ctx.plan_run.id),
        )
        print("🔍 Creating clarification")
        return clarification
