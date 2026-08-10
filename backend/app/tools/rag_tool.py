from app.rag.embeddings import create_embedding
from app.rag.vector_store import search_documents


def search_medical_documents(
    query: str,
    limit: int = 3,
    case_id: int | None = None
):
    """
    Search medical documents using RAG.

    If case_id is provided, only documents
    belonging to that case are searched.
    """

    embedding = create_embedding(
        query
    )

    results = search_documents(
        embedding=embedding,
        limit=limit,
        case_id=case_id
    )

    return results
