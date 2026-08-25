import os

import requests


OLLAMA_EMBED_URL = os.getenv(
    "OLLAMA_EMBED_URL",
    "http://localhost:11434/api/embed"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text:latest"
)


def create_embedding(text: str) -> list[float]:
    """
    Erstellt ein Embedding über Ollama.
    """

    if not text or not text.strip():
        return []

    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    embeddings = data.get("embeddings")

    if not embeddings:
        raise RuntimeError(
            "Ollama returned no embeddings"
        )

    return embeddings[0]
