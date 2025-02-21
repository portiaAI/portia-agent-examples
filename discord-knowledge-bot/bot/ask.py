"""Simple Ask RAG Interface."""

from portia.config import Config, LLMModel, LogLevel
from portia.runner import Runner
from portia.tool_registry import InMemoryToolRegistry, PortiaToolRegistry
from portia.workflow import WorkflowState

from bot.weaviate import RAGQueryDBTool, close_weaviate

config = Config.from_default(
    default_log_level=LogLevel.DEBUG, llm_model_name=LLMModel.GPT_4_O
)
registry = PortiaToolRegistry(config) + InMemoryToolRegistry.from_local_tools(
    [
        RAGQueryDBTool(
            description="Used to retrieve information from the Portia SDK docs.",
        ),
    ],
)
runner = Runner(config, tools=registry)


def get_answer(question: str) -> str:
    full_question = f"Please use the Portia SDK knowledge docs and any information from Github issues to answer the following question: {question}. "
    workflow = runner.execute_query(full_question)
    if (
        workflow.state == WorkflowState.NEED_CLARIFICATION
        or workflow.state == WorkflowState.FAILED
    ):
        return "Sorry, I wasn't able to find an answer"
    if workflow.outputs.final_output:
        return f"""Question: {question}\nAnswer: {str(workflow.outputs.final_output.value)}"""
    return "Sorry,  I wasn't able to find an answer"


if __name__ == "__main__":
    # Use for local testing
    try:
        print(get_answer("What types of storage class can I use with the Porita SDK?"))
    finally:
        close_weaviate()
