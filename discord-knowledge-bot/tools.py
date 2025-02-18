from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from typing import TypedDict

from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from pydantic import BaseModel, Field
from portia.config import Config
import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
from portia.execution_context import ExecutionContext, empty_context
from portia.llm_wrapper import LLMWrapper
from portia.tool import Tool
import os
from markdownify import markdownify as md
from dotenv import load_dotenv
from weaviate.classes.init import Auth
import time
load_dotenv(override=True)

EMBEDDING_MODEL = "text-embedding-3-large"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_FUNCTION = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
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
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
WEAVIATE_CLIENT = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL, auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
    headers = {"X-OpenAI-Api-Key": OPENAI_API_KEY}
)
while not WEAVIATE_CLIENT.is_ready():
    print("Waiting for Weaviate to be ready...")
    time.sleep(1)
    
PORTIA_SDK_DOCS = WEAVIATE_CLIENT.collections.get("SDK_Docs")

class WebDocumentLoaderTool(Tool[list[Document]]):
    """Loads documents from the web for RAG."""

    id: str = "web_document_loader_tool"
    name: str = "Web Document Loader Tool"
    output_schema: tuple[str, str] = (
        "list[Document]",
        "list[Document]: list of the documents loaded from the web",
    )
    domains: set[str] = {"https://docs.portialabs.ai"}

    def run(self, _: ExecutionContext) -> list[Document]:
        """Run the Web Document Loader Tool."""
        all_docs = []
        for domain in self.domains:
            loader = RecursiveUrlLoader(url=domain)
            docs = loader.load()
            all_docs.extend(docs)
        for doc in all_docs:
            doc.id = doc.metadata["source"]
        return all_docs


class RAGEmbedderDBToolSchema(BaseModel):
    """Input for RAGDocumentLoaderTool."""

    documents: list[Document] = Field(
        ...,
        description=("The documents to load."),
    )


class RAGEmbedderDBTool(Tool[str]):
    """Uses RAG to embed documents."""

    id: str = "rag_embedder_tool"
    name: str = "RAG Embedder Tool"
    args_schema: type[BaseModel] = RAGEmbedderDBToolSchema
    output_schema: tuple[str, str] = ("str", "str: output of the search results")

    def run(self, _: ExecutionContext, documents: list[Document]) -> None:
        """Run the RAG Embedder Tool."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        for doc in documents:
            doc.page_content = md(doc.page_content)
        all_splits = text_splitter.split_documents(documents)
        for split in all_splits:
            PORTIA_SDK_DOCS.data.insert({
                "text": split.page_content,
                "metadata": split.metadata,
            })


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
    output_schema: tuple[str, str] = ("str", "str: output of the search results")

    def run(self, _: ExecutionContext, question: str) -> str:
        """Run the RAG Query Tool."""

        class State(TypedDict):
            question: str
            context: list[Document]
            answer: str

        llm = LLMWrapper(Config.from_default()).to_langchain()

        # Define application steps
        def retrieve(state: State):
            vector_store = WeaviateVectorStore(
                client=WEAVIATE_CLIENT,
                index_name="SDK_Docs", # name of the collection in Weaviate
                text_key="text", # 'text' is name of the text field in the collection
                embedding=EMBEDDING_FUNCTION,
            )
            docs = vector_store.similarity_search(question)
            return {"context": docs}

        def generate(state: State):
            docs_content = "\n\n".join(doc.page_content for doc in state["context"])
            messages = RETRIEVAL_PROMPT.invoke(
                {"question": state["question"], "context": docs_content}
            )
            response = llm.invoke(messages)
            links = [
                f"[{doc.metadata['metadata']['title']}]({doc.metadata['metadata']['source']})"
                for doc in state["context"]
            ]
            links = set(links)
            if links:
                answer = f"{response.content}\n\nLinks:\n{'\n'.join(links)}"
            else:
                answer = response.content
            return {"answer": answer}

        # Compile application and test
        graph_builder = StateGraph(State).add_sequence([retrieve, generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        output = graph.invoke({"question": question})
        return output["answer"]


if __name__ == "__main__":
    # test the RAGQueryDBTool by calling it directly, bit of a hack
    print(RAGQueryDBTool().run(empty_context(), question="What is the Portia SDK?"))
