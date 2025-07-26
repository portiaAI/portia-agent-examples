from typing import Dict
import json
from pydantic import BaseModel, Field
from portia import Tool, ToolRunContext, MultipleChoiceClarification


class GroceryToolSchema(BaseModel):
    """Schema defining the inputs for the GroceryTool."""

    results: str = Field(
        ...,
        description="JSON string containing search results with product names and prices",
    )
    choice: str | None = Field(None, description="User's choice from the alternatives")


class GroceryTool(Tool[Dict[str, str]]):
    """Shows product alternatives and gets user choice"""

    id: str = "alternatives"
    name: str = "Product Alternatives Tool"
    description: str = "Shows alternatives and gets user choice"
    args_schema: type[BaseModel] = GroceryToolSchema
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
        self, ctx: ToolRunContext, results: str, choice: str | None = None
    ) -> Dict[str, str] | MultipleChoiceClarification:
        """Handle product alternatives through clarification"""
        if choice:
            print(f"User chose: {choice}")
            return {"product": choice.split(" - ")[0]}

        print(f"🔍 Processing results: {results}")

        try:
            data = json.loads(results)
            products = data["results"]
            alternative = data["alternative"]
            print(f"🔍 Alternative: {alternative}")
            if not alternative:
                print("🔍 Product is available")
                return {"product": products[0]["name"]}
            print(f"🔍 Parsed products: {products}")
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"Failed to parse results: {e}")
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

        clarification = MultipleChoiceClarification(
            user_guidance="Choose which item you'd like to add to cart:",
            options=options,
            argument_name="choice",
            plan_run_id=str(ctx.plan_run.id),
        )
        print("🔍 Creating clarification")
        return clarification
