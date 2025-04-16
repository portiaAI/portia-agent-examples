import os
from typing import Literal, Type

import portia.tool
from dotenv import load_dotenv
from portia import (
    Config,
    DefaultToolRegistry,
    InMemoryToolRegistry,
    McpToolRegistry,
    Portia,
    Tool,
    ToolRunContext,
)
from portia.cli import CLIExecutionHooks
from pydantic import BaseModel, Field

portia.tool.MAX_TOOL_DESCRIPTION_LENGTH = 2048


class RefundHumanApprovalInput(BaseModel):
    """Input for the HumanApprovalTool."""

    refund_request: str = Field(
        ..., description="The exact refund request from the customer"
    )
    summary: str = Field(
        ...,
        description="A summary of the reasoning for the approval decision.",
    )
    human_decision: Literal["APPROVED", "REJECTED"] | None = Field(
        None,
        description=(
            "Whether we have already approved the refund.\n"
            "This MUST be set to None until the clarification check has been done.\n"
            "If the human approves, this value will be 'APPROVED'.\n"
            "If the human rejects, this value will be 'REJECTED'."
        ),
    )


class RefundHumanApprovalTool(Tool[str]):
    """
    A tool to request human approval before proceeding with a refund, given a rationale from the Agent.

    Given a summary of the reasoning for the approval decision, the human will approve or reject the request.
    This tool does not actually issue the refund.
    """

    id: str = "human_approval"
    name: str = "Human Approval"
    description: str = "A tool to request human approval in order to continue. Given a summary of the reasoning for the approval decision, the human will approve or reject the request."
    args_schema: Type[BaseModel] = RefundHumanApprovalInput
    output_schema: tuple[str, str] = (
        "str",
        "APPROVED or REJECTED depending on the human decision",
    )

    def run(
        self,
        context: ToolRunContext,
        refund_request: str,
        summary: str,
        human_decision: Literal["APPROVED", "REJECTED"] | None = None,
    ) -> bool:
        return False


class RefundReviewerInput(BaseModel):
    """Input for the RefundReviewerTool."""

    refund_request: str = Field(
        description="The exact refund request from the customer"
    )
    refund_policy: str = Field(description="The refund policy for the product")


class RefundReviewerTool(Tool[str]):
    """
    A tool to review a refund request from a customer against the refund policy

    This tool calls an LLM to assess the refund request against the refund policy and
    either:

    - Make a recommendation to approve it.
    - Reject the request and exit with an error message containing the reason for the rejection.

    NB. This tool does not actually process the refund.
    """

    id: str = "refund_reviewer"
    name: str = "Refund Reviewer"
    description: str = (
        "A tool to review a refund request from a customer against "
        "the refund policy and decide if it gets approved or rejected. This tool does "
        "not actually process the refund."
    )
    args_schema: Type[BaseModel] = RefundReviewerInput
    output_schema: tuple[str, str] = (
        "json",
        "A JSON object with the following fields: 'decision' (str: 'APPROVED' or 'REJECTED'), 'reason' (str: the reason for the decision)",
    )

    def run(
        self,
        context: ToolRunContext,
        refund_request: str,
        refund_policy: str,
    ) -> bool:
        return False


config = Config.from_default(default_log_level="INFO")

tools = (
    McpToolRegistry.from_stdio_connection(
        server_name="stripe",
        command="npx",
        args=[
            "-y",
            "@stripe/mcp",
            "--tools=all",
            f"--api-key={os.environ['STRIPE_TEST_API_KEY']}",
        ],
    )
    + DefaultToolRegistry(
        config=config,
    )
    + InMemoryToolRegistry.from_local_tools(
        [RefundReviewerTool(), RefundHumanApprovalTool()]
    )
)


def init_portia():
    load_dotenv(override=True)

    portia_instance = Portia(
        config=config, tools=tools, execution_hooks=CLIExecutionHooks()
    )

    return portia_instance
