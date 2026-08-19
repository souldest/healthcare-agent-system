from fastapi import FastAPI

from app.api import agents
from app.api import patients
from app.api import cases
from app.api import documents
from app.api import rag
from app.api import insurer
from app.api import member


app = FastAPI(
    title="Healthcare Agent System",
    description="Multi-Agent AI Platform",
    version="0.1.0"
)


app.include_router(
    patients.router
)

app.include_router(
    cases.router
)

app.include_router(
    documents.router
)

app.include_router(
    rag.router
)

app.include_router(
    agents.router
)

app.include_router(
    insurer.router
)

app.include_router(
    member.router
)

@app.get("/")
def root():
    return {
        "application": "Healthcare Agent System",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "database": "ready",
        "agents": "ready"
    }
