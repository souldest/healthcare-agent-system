import os

import chromadb


COLLECTION_NAME = "medical_documents"


def get_chroma_client():
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8004"))

    return chromadb.HttpClient(
        host=host,
        port=port,
    )


def get_collection():
    client = get_chroma_client()

    return client.get_or_create_collection(
        name=COLLECTION_NAME
    )


def add_document(
    document_id: str,
    content: str,
    embedding: list[float],
    metadata: dict,
):
    collection = get_collection()

    normalized_metadata = dict(metadata)

    if "case_id" in normalized_metadata:
        normalized_metadata["case_id"] = str(
            normalized_metadata["case_id"]
        )

    collection.upsert(
        ids=[str(document_id)],
        documents=[content],
        embeddings=[embedding],
        metadatas=[normalized_metadata],
    )


def search_documents(
    embedding: list[float],
    limit: int = 3,
    case_id: int | None = None,
):
    collection = get_collection()

    query_kwargs = {
        "query_embeddings": [embedding],
        "n_results": limit,
    }

    if case_id is not None:
        query_kwargs["where"] = {
            "case_id": str(case_id)
        }

    return collection.query(**query_kwargs)
