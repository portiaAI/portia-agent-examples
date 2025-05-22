from pydantic import BaseModel, Field
from typing import Any
from portia import (
    Config,
    InMemoryToolRegistry,
    LLMTool,
    Message,
    PlanBuilder,
    Tool,
    Portia,
    ToolHardError,
    ToolRunContext,
    Variable,
)


class CustomerProfile(BaseModel):
    id: str
    name: str


class RiskProfile(BaseModel):
    risk_class: str = Field(
        ...,
        description="The type of the specific risk matched, one of PEP, adverse-media, sanctions, AML.",
    )
    details: dict[str, Any] = Field(
        ...,
        description="The details of the specific risk matched.",
    )


class ProfileMatch(BaseModel):
    matched_name: str = Field(
        ...,
        description="The name matched.",
    )
    risk_details: list[RiskProfile] = Field(
        ..., description="The set of risks matched for this profile"
    )


CUSTOMERS = [
    CustomerProfile(id="cus-123", name="Keir Starmer"),
]


RISK_PROFILES = [
    ProfileMatch(
        matched_name="Keir Starmer",
        risk_details=[
            RiskProfile(
                risk_class="PEP",
                details={
                    "pep_status": {
                        "is_pep": True,
                        "pep_class": "CLASS ONE",
                        "pep_type": "Domestic PEP",
                        "reason": "Prime Minister, Former Leader of the Opposition, Member of Parliament (MP)",
                        "position": "Prime Minister, Leader of the Labour Party",
                        "jurisdiction": "United Kingdom",
                        "since": "2020-04-04",
                        "last_updated": "2025-05-01",
                    },
                    "source": {
                        "provider": "DemoKYCWatchlist",
                        "source_name": "Global PEP List",
                        "source_url": "https://example-kyc-provider.com/pep/keir-starmer",
                        "retrieved_at": "2025-05-21T10:30:00Z",
                    },
                    "risk_score": 60,
                    "risk_level": "Medium",
                    "match_confidence": 95,
                    "comments": "Identified as a domestic PEP due to his senior political position within the UK government. No adverse media or sanctions detected.",
                    "flags": ["PEP"],
                },
            ),
            RiskProfile(
                risk_class="adverse-media",
                details={
                    "adverse_media": {
                        "last_5_articles": [
                            "Politics latest: Judge clears way for Keir Starmer to sign Chagos Islands deal",
                            "The UK risks falling apart. Keir Starmer can mend it now - but he doesn't have much time | Martin Kettle",
                            "UK Prime Minister Keir Starmer reverses course on winter fuel payments",
                            "Net migration halved last year in boost to Keir Starmer",
                            "Starmer defends courts over Lucy Connolly racist post",
                        ]
                    },
                    "source": {
                        "provider": "Internal ",
                        "source_name": "Media Watchlist",
                        "source_url": "https://example-kyc-provider.com/adverse-media/keir-starmer",
                        "retrieved_at": "2025-07-21T10:30:00Z",
                    },
                    "risk_score": 20,
                    "risk_level": "Low",
                    "match_confidence": 87,
                    "comments": "Media detected from multiple sources.",
                    "flags": ["adverse-media"],
                },
            ),
        ],
    )
]

FILTER_POLICY = """
When reviewing KYC risks use this policy to determine if the risk should be filtered or not.

You should only focus on one risk type at a time. 

If the risk type requested is not in the given risk profile return NO_RESULT

If the risk includes PEP (Politically Exposed Person):
- We only care if the PEP is class ONE. If not return FILTERED
- We only care if the PEP is from the UK. If not returned FILTERED
- Otherwise return NOT_FILTERED.

If the risk includes adverse media:
- We only care about high severity adverse media (terrorism, violence, other serious crime). If the links
do not indicate this return FILTERED.
- Else return NOT_FILTERED

If the risk includes sanctions:
- return NOT_FILTERED

If the risk includes AML:
- return NOT_FILTERED

If the risk does not match these categories return NO_RESULT

When coming up with a FINAL RECOMMENDATION: 
- If all status checks are FILTERED return FILTERED
- If some status checks are FILTERED but some are NOT_FILTERED return NOT_FILTERED
- If all status checks are NOT_FILTERED return NOT_FILTERED
- You can ignore status checks which return NO_RESULT
"""


class CustomerLoadingToolSchema(BaseModel):
    """Input for CustomerLoadingTool."""

    customer_id: str = Field(
        ...,
        description=("The id of the customer to load data for"),
    )


class CustomerLoadingTool(Tool):
    id: str = "load-customer-tool"
    name: str = "Customer Loading Tool"
    description: str = "Used to load data on a specific customer"
    args_schema: type[BaseModel] = CustomerLoadingToolSchema
    output_schema: tuple[str, str] = (
        "CustomerProfile",
        "The details of the customer.",
    )

    def run(self, _: ToolRunContext, customer_id: str) -> CustomerProfile:
        for customer in CUSTOMERS:
            if customer.id == customer_id:
                return customer

        raise ToolHardError(f"customer with id {customer_id} not found")


class RiskMatchingToolSchema(BaseModel):
    """Input for RiskMatchingTool."""

    customer_profile: CustomerProfile = Field(
        ...,
        description=("The profile of the customer to match"),
    )


class RiskMatchingTool(Tool):
    id: str = "risk-matching-tool"
    name: str = "Risk Matching Tool"
    description: str = "Used to return risk profiles that match the given customer"
    args_schema: type[BaseModel] = RiskMatchingToolSchema
    output_schema: tuple[str, str] = (
        "str",
        "The location of the output audio file.",
    )

    def run(
        self, _: ToolRunContext, customer_profile: CustomerProfile
    ) -> list[ProfileMatch]:
        profiles_to_return = []
        for profile in RISK_PROFILES:
            if profile.matched_name == customer_profile.name:
                profiles_to_return.append(profile)

        return profiles_to_return


class FilterPolicyLoadingTool(Tool):
    id: str = "filter-policy-loading-tool"
    name: str = "Filter Policy Loading Tool"
    description: str = "A tool that loads the filter policy to use."
    output_schema: tuple[str, str] = (
        "str",
        "The filter policy to use.",
    )

    def run(self, _: ToolRunContext) -> str:
        return FILTER_POLICY


class RiskFilteringAgentSchema(BaseModel):
    """Input for RiskFilteringAgent."""

    customer_profile: CustomerProfile = Field(
        ...,
        description=("The profile of the customer to run filtering on"),
    )
    risk_profile: ProfileMatch = Field(
        ...,
        description=("The matched profile to run filtering on"),
    )


class RiskFilteringAgentOutputSchema(BaseModel):
    result: str = Field(
        ...,
        description="The final result of the agent. Should be one of FILTERED, NOT_FILTERED or NO_RESULT.",
    )

    explanation: str = Field(
        ..., description="A human readable explanation of the final result."
    )


class FilteringStepTool(LLMTool):
    id: str = "filtering-step-tool"
    prompt: str = """You are a KYC agent tasked with reviewing alerts. An alert consists of:
    - A customer profile provided from the bank or financial institution.
    - A risk_profile which contains information matched to the given customer profile.

    Your job is to take these two data points and a filter policy and decide if according to the 
    policy given the alert should be filtered or not.

    IMPORTANT: You will be asked to reason about one type of risk at a time. Please focus only 
    on this type of risk ignoring other parts of the policy.

    You should return one of FILTERED, NOT_FILTERED or NO_RESULT based on the details provided to you.
    
    Its safe to default to NOT_FILTERED if you're not sure.
    """

    def run(  # type: ignore
        self, ctx: ToolRunContext, task: str, task_data: list[Any] | str | None = None
    ) -> RiskFilteringAgentOutputSchema:
        """Run the LLMTool."""
        model = ctx.config.get_planning_model() or ctx.config.get_default_model()

        context = (
            "Additional context for the LLM tool to use to complete the task, provided by the "
            "run information and results of other tool calls. Use this to resolve any "
            "tasks"
        )

        task_data_str = self.process_task_data(task_data)

        task_str = task
        if task_data_str:
            task_str += f"\nTask data: {task_data_str}"
        if self.tool_context:
            context += f"\nTool context: {self.tool_context}"
        content = (
            task_str if not len(context.split("\n")) > 1 else f"{context}\n\n{task_str}"
        )
        messages = [
            Message(role="user", content=self.prompt),
            Message(role="user", content=content),
        ]
        response = model.get_structured_response(
            messages,
            RiskFilteringAgentOutputSchema,
        )
        return response


if __name__ == "__main__":
    tools = InMemoryToolRegistry.from_local_tools(
        [
            CustomerLoadingTool(),
            RiskMatchingTool(),
            FilterPolicyLoadingTool(),
            FilteringStepTool(),
        ]
    )
    portia = Portia(
        config=Config.from_default(
            default_log_level="DEBUG",
            execution_agent_type="ONE_SHOT",
        ),
        tools=tools,
    )

    plan_builder = PlanBuilder(
        query="Load the data for the customer id given in the inputs, call the risk matching tool with it. Then pass the customer and risk to the filtering agent."
    )

    plan_builder.plan_input(
        name="customer_id",
        description="The id of the customer to run the agent for",
    )

    plan_builder.step(
        task="Call the customer loading tool with the customer_id in the inputs",
        tool_id="load-customer-tool",
        inputs=[
            Variable(
                name="customer_id",
                description="The customer_id taken from the plan run inputs.",
            )
        ],
        output="$customer_data",
    )
    plan_builder.step(
        task="Call the risk matching tool with the given $customer_data",
        tool_id="risk-matching-tool",
        output="$matched_risk",
        inputs=[
            Variable(
                name="$customer_data",
                description="The customer data to match against.",
            )
        ],
    )

    plan_builder.step(
        task="Load the filter policy",
        tool_id="filter-policy-loading-tool",
        output="$filter_policy",
    )

    plan_builder.step(
        task="Reason about the PEP logic ONLY based on the given policy, customer and risk",
        inputs=[
            Variable(
                name="$customer_data",
                description="The customer data to use",
            ),
            Variable(
                name="$matched_risk",
                description="The risk data to use",
            ),
            Variable(
                name="$filter_policy",
                description="The filter policy to use when analyzing the customer + risk.",
            ),
        ],
        tool_id="filtering-step-tool",
        output="$pep_status",
    )

    plan_builder.step(
        task="Reason about the adverse media logic ONLY based on the given policy, customer and risk",
        inputs=[
            Variable(
                name="$customer_data",
                description="The customer data to use",
            ),
            Variable(
                name="$matched_risk",
                description="The risk data to use",
            ),
            Variable(
                name="$filter_policy",
                description="The filter policy to use when analyzing the customer + risk.",
            ),
        ],
        tool_id="filtering-step-tool",
        output="$adverse_media_status",
    )

    plan_builder.step(
        task="Reason about the sanctions logic ONLY based on the given policy, customer and risk",
        inputs=[
            Variable(
                name="$customer_data",
                description="The customer data to use",
            ),
            Variable(
                name="$matched_risk",
                description="The risk data to use",
            ),
            Variable(
                name="$filter_policy",
                description="The filter policy to use when analyzing the customer + risk.",
            ),
        ],
        tool_id="filtering-step-tool",
        output="$sanctions_status",
    )

    plan_builder.step(
        task="Reason about the AML logic ONLY based on the given policy, customer and risk",
        inputs=[
            Variable(
                name="$customer_data",
                description="The customer data to use",
            ),
            Variable(
                name="$matched_risk",
                description="The risk data to use",
            ),
            Variable(
                name="$filter_policy",
                description="The filter policy to use when analyzing the customer + risk.",
            ),
        ],
        tool_id="filtering-step-tool",
        output="$aml_status",
    )

    plan_builder.step(
        task="Come up with a final recommendation based on the given inputs.",
        tool_id="filtering-step-tool",
        inputs=[
            Variable(
                name="$filter_policy",
                description="The filter policy to use when analyzing the customer + risk.",
            ),
            Variable(
                name="$pep_status",
                description="The output of the PEP check",
            ),
            Variable(
                name="$adverse_media_status",
                description="The output of the adverse_media_check",
            ),
            Variable(
                name="$sanctions_status",
                description="The output of the sanctions_check",
            ),
            Variable(
                name="$aml_status",
                description="The output of the aml_check",
            ),
        ],
        output="$final_recommendation",
    )

    plan = plan_builder.build()

    final_output = portia.run_plan(
        plan,
        plan_run_inputs={"customer_id": "cus-123"},
    )

    final_output = final_output.outputs.final_output
    if not final_output:
        raise ValueError("Agent returned unexpected empty output")
    print(final_output)
