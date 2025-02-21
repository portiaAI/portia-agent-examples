import os
import time

import weaviate
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from markdownify import markdownify as md
from portia.execution_context import ExecutionContext, empty_context
from portia.tool import Tool
from pydantic import BaseModel, Field
from tqdm import tqdm
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.init import Auth

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTORISER_CONFIG = Configure.Vectorizer.text2vec_openai(
    model="text-embedding-3-large",
    dimensions=1024,  # Choose from 256, 1024, or 3072
)
RETRIEVAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "human",
            """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
            Question: {question},
            Context: {context} ,
            Answer:""",
        ),
    ],
)
if "localhost" in os.getenv("WEAVIATE_URL"):
    WEAVIATE_CLIENT = weaviate.connect_to_local(
        headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
    )
else:
    WEAVIATE_CLIENT = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
        headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
    )

while not WEAVIATE_CLIENT.is_ready():
    print("Waiting for Weaviate to be ready...")
    time.sleep(1)

SDK_DOCS_COLLECTION_NAME = "SDK_Docs"
DOCS_COLLECTION = WEAVIATE_CLIENT.collections.get(SDK_DOCS_COLLECTION_NAME)
if not DOCS_COLLECTION.exists():
    print("Creating Weaviate collection...")
    WEAVIATE_CLIENT.collections.create(
        name=SDK_DOCS_COLLECTION_NAME,
        vectorizer_config=VECTORISER_CONFIG,
        properties=[
            Property(name="text", data_type=DataType.TEXT),
            Property(
                name="metadata",
                data_type=DataType.OBJECT,
                nested_properties=[
                    Property(name="name", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                    Property(name="content_type", data_type=DataType.TEXT),
                ],
            ),
        ],
    )


def insert_docs_into_weaviate(documents: list[Document]):
    """Insert documents into Weaviate."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    for doc in documents:
        doc.page_content = md(doc.page_content)
    all_splits = text_splitter.split_documents(documents)
    for split in tqdm(all_splits, desc="Inserting documents", unit="chunk"):
        DOCS_COLLECTION.data.insert(
            {
                "text": split.page_content,
                "metadata": split.metadata,
            }
        )


def close_weaviate():
    WEAVIATE_CLIENT.close()


class RAGQueryDBToolSchema(BaseModel):
    """Input for RAGQueryTool."""

    question: str = Field(
        ...,
        description=("The question to search for in the given doc source."),
    )


class RAGQueryDBTool(Tool[str]):
    """Uses RAG to answer questions."""

    id: str = "rag_query_tool"
    name: str = "RAG Query Tool"
    description: str = "Used to retrieve information from the Portia SDK docs."
    args_schema: type[BaseModel] = RAGQueryDBToolSchema
    output_schema: tuple[str, str] = (
        "list",
        "A list of results relevant to the query.",
    )

    def run(self, _: ExecutionContext, question: str) -> str:
        """Run the RAG Query Tool."""

        result = DOCS_COLLECTION.query.near_text(
            query=question,
            limit=5,
            return_properties=["text"],
        )
        return [obj.properties["text"] for obj in result.objects]


if __name__ == "__main__":
    try:
        # Can be used for local testing of the tool
        print(RAGQueryDBTool().run(empty_context(), question="What is the Portia SDK?"))
    finally:
        close_weaviate()
