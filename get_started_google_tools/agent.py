import sys

from firecrawl import FirecrawlApp
from portia import Config, InMemoryToolRegistry, LogLevel, Portia, Tool, ToolRunContext
from portia.cli import CLIExecutionHooks
from pydantic import BaseModel, Field


class ScrapeToolSchema(BaseModel):
    """Schema for the ScrapeTool."""

    url: str = Field(
        ...,
        description="The URL to scrape.",
    )


# Crew equivalent: https://docs.firecrawl.dev/integrations/crewai
class ScrapeTool(Tool[str]):
    """Tool to retrieve membership ID from Everyone Active."""

    id: str = "scrape_tool"
    name: str = "Scrape Tool"
    description: str = "Scrape a given URL"
    args_schema: type[BaseModel] = ScrapeToolSchema
    output_schema: tuple[str, str] = ("str", "the scraped text")

    def get_auth_cookie(
        self,
    ) -> str:
        """Get the auth cookie."""
        # TODO: Implement this method using a browser to login and then get the cookier
        pass

    def run(
        self,
        context: ToolRunContext,
        url: str,
    ) -> str:
        # headers = {"Cookie": get_auth_cookie()}

        data = app.scrape_url(
            url,
            params={"limit": 100, "scrapeOptions": {"formats": ["markdown", "html"]}},
            poll_interval=30,
        )
        print(data)
        return data


app = FirecrawlApp(api_key="", api_url="localhost:3002")

task = (
    "Scrape all sanctioned people from https://search-uk-sanctions-list.service.gov.uk/"
)

if __name__ == "__main__":
    my_config = Config.from_default(
        llm_model_name="o_3_mini",
        log_level=LogLevel.DEBUG,
    )
    portia = Portia(
        config=my_config,
        tools=InMemoryToolRegistry.from_local_tools([ScrapeTool()]),
        execution_hooks=CLIExecutionHooks(),
    )
    plan = portia.plan(task)
    print("\nHere are the steps in the generated plan:")
    [print(step.model_dump_json(indent=2)) for step in plan.steps]
    user_input = input("Are you happy with the plan? (y/n):\n")
    if user_input != "y":
        sys.exit()
    print("\nThe plan will now be executed. Please wait...")
    plan_run = portia.run_plan(plan)

    # Serialise into JSON and print the output
    print(f"{plan_run.model_dump_json(indent=2)}")
