import argparse
import json
import os
from typing import Literal, Type
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage

from portia import (
    DefaultToolRegistry,
    InMemoryToolRegistry,
    MultipleChoiceClarification,
    Portia,
    McpToolRegistry,
    Config,
    Tool,
    ToolHardError,
    ToolRunContext,
    execution_context,
)
import portia.tool
from portia.cli import CLIExecutionHooks
from pydantic import BaseModel, Field
from portia.llm_wrapper import LLMWrapper
from portia.config import LLM_TOOL_MODEL_KEY


portia.tool.MAX_TOOL_DESCRIPTION_LENGTH = 2048


class RefundHumanApprovalInput(BaseModel):
    """Input for the HumanApprovalTool."""

    refund_request: str = Field(
        ..., description="The exact refund request from the customer"
    )
    summary: str = Field(
        ..., description="A summary of the reasoning for the approval decision."
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
        if human_decision is None:
            return MultipleChoiceClarification(
                plan_run_id=context.plan_run_id,
                user_guidance=(
                    "User refund request:\n"
                    f"{refund_request}\n\n"
                    "---\n\n"
                    "Suggestion: Approve the refund request.\n\n"
                    "Reasoning:\n"
                    f"{summary}\n\n"
                    "---\n\n"
                    "You can choose to APPROVE or REJECT the refund."
                ),
                argument_name="human_decision",
                options=["APPROVED", "REJECTED"],
            )
        return human_decision


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
        llm = LLMWrapper.for_usage(LLM_TOOL_MODEL_KEY, context.config).to_langchain()
        messages = [
            SystemMessage(
                content="You are a helpful assistant that carefully reviews refund requests from customers against "
                "the refund policy, and provides a break down of your reasoning about what the decision should be.\n"
                "Following your detailed analysis, you will respond with a single word: 'APPROVED' or 'REJECTED' on a new line.\n"
                "The refund policy is as follows:\n"
                f"{refund_policy}\n"
            ),
            HumanMessage(
                content=f"The refund request is as follows:\n{refund_request}"
            ),
        ]
        response = llm.invoke(messages)
        llm_decision = response.content.split("\n")[-1].strip()
        if llm_decision == "APPROVED":
            return json.dumps({"decision": "APPROVED", "reason": response.content})
        elif llm_decision == "REJECTED":
            return json.dumps({"decision": "REJECTED", "reason": response.content})
        else:
            raise ToolHardError("Invalid LLM decision: " + llm_decision)


def main(customer_email: str):
    with open("inbox.txt", "w") as f:
        f.write(customer_email)

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

    portia = Portia(config=config, tools=tools, execution_hooks=CLIExecutionHooks())
    # Run the test query and print the output!
    with execution_context(
        additional_data={
            "Stripe MCP tool guidance": "If you encounter tools that require a limit argument, "
                                        "ALWAYS USE A VALUE OF 1."
        }
    ):
        plan = portia.plan(
            """
Read the refund request email from the customer and decide if it should be approved or rejected.
If you think the refund request should be approved, check with a human for final approval and then process the refund.

Stripe instructions:
* Customers can be found in Stripe using their email address.
* The payment can be found against the Customer.
* Refunds can be processed by creating a refund against the payment.

The refund policy can be found in the file: ./refund_policy.txt

The refund request email can be found in "inbox.txt" file
"""
        )
        print("Plan:")
        print(plan.pretty_print())
        portia.run_plan(plan)


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="The email address of the customer. Should match the email address in Stripe.",
    )
    parser.add_argument(
        "--request",
        type=str,
        required=False,
        default="I bought one of your hoverboards 3 days ago. "
        "When I took it out of the box and turned it on, "
        "it did not work. Please can I get a refund?",
    )

    args = parser.parse_args()
    main(f"""---header---
        From: Marty McFly <email: {args.email}>
        To: support@hoverfly.com
        Subject: Refund request
        ---header---
        ---body---
        Hi,
        {args.request}

        Thanks,
        Marty McFly
        ---body---""")
