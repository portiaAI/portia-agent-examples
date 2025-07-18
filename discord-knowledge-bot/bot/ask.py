"""Simple Ask RAG Interface."""

from portia import (
    Config,
    InMemoryToolRegistry,
    LogLevel,
    PlanRunState,
    Portia,
    PortiaToolRegistry,
)

from bot.weaviate import RAGQueryDBTool, close_weaviate

config = Config.from_default(
    default_log_level=LogLevel.DEBUG,
    default_model="openai/gpt-4o",
)
registry = PortiaToolRegistry(config) + InMemoryToolRegistry.from_local_tools(
    [
        RAGQueryDBTool(
            description="Used to retrieve information from the Portia SDK docs.",
        ),
    ],
)
portia = Portia(config, tools=registry)


def get_answer(question: str) -> str | None:
    full_question = (
        "Please use the Portia SDK knowledge docs from the RAG DB to answer the following "
        f"question: {question}. Write a summary of the answer in under 2000 characters. "
    )
    run = portia.run(full_question)
    if run.state == PlanRunState.NEED_CLARIFICATION or run.state == PlanRunState.FAILED:
        return None
    if run.outputs.final_output:
        return str(run.outputs.final_output.value)
    return None


if __name__ == "__main__":
    # Use for local testing
    try:
        print(get_answer("What types of storage class can I use with the Porita SDK?"))
    finally:
        close_weaviate()
