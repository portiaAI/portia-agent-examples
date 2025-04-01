from typing import Any
from dotenv import load_dotenv
from openai import OpenAI
from portia import Config, Portia, PortiaToolRegistry
from portia.model import (
    LangChainGenerativeModel,
    Message,
    BaseModelT,
    map_message_to_instructor,
)
from portia.cli import CLIExecutionHooks

from portia.config import (
    PLANNING_MODEL_KEY,
    DEFAULT_MODEL_KEY,
    EXECUTION_MODEL_KEY,
    LLM_TOOL_MODEL_KEY,
)
from langchain_ollama import ChatOllama
from pydantic import SecretStr
import instructor


class OllamaModel(LangChainGenerativeModel):
    def __init__(self, model_name: str):
        super().__init__(client=ChatOllama(model=model_name), model_name=model_name)

    def get_structured_response(
        self, messages: list[Message], schema: type[BaseModelT], **kwargs: Any
    ) -> BaseModelT:
        client = instructor.from_openai(
            OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",  # required, but unused
            ),
            mode=instructor.Mode.JSON,
        )
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[map_message_to_instructor(message) for message in messages],
            response_model=schema,
        )
        return response


def main():
    config = Config.from_default(
        default_log_level="DEBUG",
        custom_models={
            PLANNING_MODEL_KEY: OllamaModel(model_name="qwen2.5:14b"),
            DEFAULT_MODEL_KEY: OllamaModel(model_name="qwen2.5:14b"),
            EXECUTION_MODEL_KEY: OllamaModel(model_name="qwen2.5:14b"),
            LLM_TOOL_MODEL_KEY: OllamaModel(model_name="qwen2.5:14b"),
        },
        openai_api_key=SecretStr("123"),
    )
    tools = PortiaToolRegistry(config).filter_tools(lambda tool: "github" in tool.id)

    portia = Portia(config=config, execution_hooks=CLIExecutionHooks(), tools=tools)
    plan = portia.plan(
        "Find a Github repository by astral-sh and star it", example_plans=[]
    )
    print(plan.model_dump_json(indent=2))
    portia.run_plan(plan)


if __name__ == "__main__":
    load_dotenv()
    main()
