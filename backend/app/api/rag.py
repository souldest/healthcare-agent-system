from fastapi import APIRouter

from app.rag.embeddings import create_embedding
from app.rag.vector_store import search_documents


router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


@router.get("/search")
def rag_search(
    q: str,
    case_id: int | None = None
):
    """
    Search medical documents using RAG.

    If case_id is provided, only documents
    belonging to that case are searched.
    """

    embedding = create_embedding(
        q
    )

    results = search_documents(
        embedding=embedding,
        limit=3,
        case_id=case_id
    )

    return results

