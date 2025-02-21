from dotenv import load_dotenv
from langchain_community.document_loaders import RecursiveUrlLoader

from bot.weaviate import close_weaviate, insert_docs_into_weaviate

load_dotenv(override=True)


def load_docs_into_weaviate(domains: list[str]):
    """Load the Portia SDK docs into a vector database."""

    all_docs = []
    for domain in domains:
        loader = RecursiveUrlLoader(url=domain)
        docs = loader.load()
        all_docs.extend(docs)
    for doc in all_docs:
        doc.id = doc.metadata["source"]
    insert_docs_into_weaviate(all_docs)


if __name__ == "__main__":
    domains = {"https://docs.portialabs.ai"}
    try:
        load_docs_into_weaviate(domains)
    finally:
        close_weaviate()
