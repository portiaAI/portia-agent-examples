from portia import Portia, PlanRunState, PlanBuilder, Config
from portia.open_source_tools.llm_tool import LLMTool
from pydantic import BaseModel, Field
from enum import Enum
from dotenv import load_dotenv

load_dotenv(override=True)
config = Config.from_default()
portia = Portia(config=config)

class Sizing(Enum):
    """The size of the planning poker estimate"""
    ONE_DAY = "1D"
    THREE_DAYS = "3D"
    FIVE_DAYS = "5D"
    SEVEN_DAYS = "7D"
    TEN_DAYS = "10D"
    TOO_LARGE_TO_ESTIMATE = "TLTE"

class PlanningPokerEstimate(BaseModel):
    """A planning poker card estimate"""
    size: Sizing = Field(..., description="The size of the planning poker card")
    reason: str = Field(..., description="Discuss the reasoning behind the estimate, any issues or assumptions you made, and any other relevant information")


class LinearTicket(BaseModel):
    """A linear ticket"""
    title: str = Field(..., description="The title of the ticket")
    description: str = Field(..., description="The description of the ticket")
    ticket_id: str = Field(..., description="The id of the ticket")

class LinearTicketList(BaseModel):
    """A list of linear tickets"""
    tickets: list[LinearTicket] = Field(..., description="The tickets")

class RepoStructure(BaseModel):
    """A structure of a repo"""
    name: str = Field(..., description="The name of the repo")
    pages: list[str] = Field(..., description="The pages of the repo")

for tool in portia.tool_registry:
    print(tool.id)

ticket_type = "Async Portia"
query = f"Get the tickets i'm working on from linear regarding {ticket_type}"
plan = PlanBuilder(
    query, structured_output_schema=LinearTicketList
).step(
    query + " and only call the tool with a limit of 10", tool_id="portia:mcp:mcp.linear.app:list_my_issues"
).step(
    f"Filter the tickets to only include the ones related to {ticket_type}", tool_id="llm_tool"
).build()
plan_run = portia.run_plan(plan)
tickets = plan_run.outputs.final_output.value.tickets
print(tickets)


with open("./context.md", "r") as f:
    codebase_context = f.read()


tool_context = f"Conform to the nearest sizing value, rounding up to the nearest day. If the ticket is too large to estimate, return TLTE.\n\n{codebase_context}"

estimate_tool = LLMTool(
    id='ticket_estimator_tool',
    name='Ticket Estimator',
)

personas = [
    "You are a frontend developer, assess the ticket and estimate with your relevant experience",
    "You are a backend developer, assess the ticket and estimate with your relevant experience",
    "You are a devops engineer, assess the ticket and estimate with your relevant experience",
]

for ticket in tickets:
    estimates = []
    estimate_plan = PlanBuilder(
        "estimate the size of the ticket", structured_output_schema=PlanningPokerEstimate
    ).step(f"Estimate the size of the ticket: {ticket.title}\n\n{ticket.description}", tool_id="ticket_estimator_tool").build()
    for persona in personas:
        context = f"""
        {persona}
        {tool_context}
        """
        estimate_tool.tool_context = context
        portia.tool_registry.with_tool(estimate_tool, overwrite=True)
        estimate = portia.run_plan(estimate_plan)
        if estimate.state == PlanRunState.COMPLETE:
            estimates.append(estimate.outputs.final_output.value)

    for estimate in estimates:
        print(f"Ticket: {ticket.title} - Estimate: {estimate.size} -\nReason: {estimate.reason}")



