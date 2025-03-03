"""Simple Ask RAG Interface."""

from portia import (
    Config,
    InMemoryToolRegistry,
    LLMModel,
    LogLevel,
    PlanRunState,
    Portia,
    PortiaToolRegistry,
)

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
portia = Portia(config, tools=registry)


def get_answer(question: str) -> str:
    full_question = f"Please use the Portia SDK knowledge docs and any information from Github issues to answer the following question: {question}. "
    run = portia.run(full_question)
    if run.state == PlanRunState.NEED_CLARIFICATION or run.state == PlanRunState.FAILED:
        return "Sorry, I wasn't able to find an answer"
    if run.outputs.final_output:
        return (
            f"""Question: {question}\nAnswer: {str(run.outputs.final_output.value)}"""
        )
    return "Sorry,  I wasn't able to find an answer"


if __name__ == "__main__":
    # Use for local testing
    try:
        print(get_answer("What types of storage class can I use with the Porita SDK?"))
    finally:
        close_weaviate()
