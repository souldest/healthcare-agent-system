from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse

from app.rag.embeddings import create_embedding
from app.rag.vector_store import add_document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/", response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):

    # 1. Save document in PostgreSQL
    db_document = Document(
        case_id=document.case_id,
        filename=document.filename,
        document_type=document.document_type,
        content=document.content
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)


    # 2. Create embedding
    embedding = create_embedding(
        document.content or ""
    )


    # 3. Store vector in ChromaDB
    add_document(
        document_id=str(db_document.id),
        content=document.content or "",
        embedding=embedding,
        metadata={
            "case_id": document.case_id,
            "filename": document.filename,
            "document_type": document.document_type
        }
    )


    # 4. Link PostgreSQL document to Chroma vector
    db_document.embedding_id = str(db_document.id)

    db.commit()
    db.refresh(db_document)


    return db_document



@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db)
):
    return db.query(Document).all()
