import os

import chromadb


CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8004"))


client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
)


collection = client.get_or_create_collection(
    name="medical_documents"
)


def add_document(
    document_id: str,
    content: str,
    embedding: list[float],
    metadata: dict,
):
    collection.add(
        ids=[document_id],
        documents=[content],
        embeddings=[embedding],
        metadatas=[metadata],
    )


def search_documents(
    embedding: list[float],
    limit: int = 3,
    case_id: int | None = None,
):
    """
    Search medical documents using semantic similarity.

    If case_id is provided, only documents belonging
    to that case are searched.
    """

    query_params = {
        "query_embeddings": [embedding],
        "n_results": limit,
    }

    if case_id is not None:
        query_params["where"] = {
            "case_id": case_id,
        }

    return collection.query(**query_params)
