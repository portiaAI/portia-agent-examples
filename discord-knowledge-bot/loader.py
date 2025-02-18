from tools import RAGEmbedderDBTool, WebDocumentLoaderTool
from portia.execution_context import empty_context
from dotenv import load_dotenv

load_dotenv(override=True)

if __name__ == "__main__":
    # Load the Portia SDK docs into a vector database.
    documents_to_load = WebDocumentLoaderTool(
        description="Used to load the Portia SDK docs from the web.",
    ).run(empty_context())
    RAGEmbedderDBTool(
        description="Used to store the Portia SDK docs in a vector database.",
    ).run(empty_context(), documents=documents_to_load)
