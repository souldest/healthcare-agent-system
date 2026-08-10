import chromadb
from chromadb.config import Settings


client = chromadb.HttpClient(
    host="healthcare-chroma",
    port=8000
)


collection = client.get_or_create_collection(
    name="medical_documents"
)


def add_document(
    document_id: str,
    content: str,
    embedding: list[float],
    metadata: dict
):
    collection.add(
        ids=[document_id],
        documents=[content],
        embeddings=[embedding],
        metadatas=[metadata]
    )


def search_documents(
    embedding: list[float],
    limit: int = 3,
    case_id: int | None = None
):
    """
    Search medical documents using semantic similarity.

    If case_id is provided, only documents belonging
    to that case are searched.
    """

    query_params = {
        "query_embeddings": [embedding],
        "n_results": limit
    }

    if case_id is not None:
        query_params["where"] = {
            "case_id": case_id
        }

    return collection.query(
        **query_params
    )

