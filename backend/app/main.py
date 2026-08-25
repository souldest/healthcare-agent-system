from fastapi import FastAPI

from app.api.patients import router as patients_router
from app.api.cases import router as cases_router
from app.api.documents import router as documents_router
from app.api.rag import router as rag_router
from app.api.agents import router as agents_router
from app.api.insurer import router as insurer_router
from app.api.member import router as member_router
from app.api.analytics import router as analytics_router


app = FastAPI(
    title="Healthcare Agent System",
    description="Multi-Agent AI Platform",
    version="0.1.0",
)


app.include_router(patients_router, prefix="/api")
app.include_router(cases_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(insurer_router, prefix="/api")
app.include_router(member_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


@app.get("/")
def root():
    return {
        "application": "Healthcare Agent System",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": "ready",
        "agents": "ready",
        "databricks": "ready",
    }
