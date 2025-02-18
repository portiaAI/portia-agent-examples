"""Simple Ask RAG Interface."""

from portia.config import Config, LogLevel
from portia.runner import Runner
from portia.workflow import WorkflowState
from portia.tool_registry import InMemoryToolRegistry
from tools import RAGQueryDBTool


runner = Runner(
    Config.from_default(default_log_level=LogLevel.DEBUG),
    tools=InMemoryToolRegistry.from_local_tools(
        [
            RAGQueryDBTool(
                description="Used to retrieve information from the Portia SDK docs.",
            ),
        ],
    ),
)


def get_answer(question: str) -> str:
    full_question = f"Please use the Portia SDK knowledge docs to answer the following question: {question}."
    workflow = runner.execute_query(full_question)
    if (
        workflow.state == WorkflowState.NEED_CLARIFICATION
        or workflow.state == WorkflowState.FAILED
    ):
        return "I wasn't able to find an answer"
    if workflow.outputs.final_output:
        return f"""Question: {question}\nAnswer: {str(workflow.outputs.final_output.value)}"""
    return "I wasn't able to find an answer"
