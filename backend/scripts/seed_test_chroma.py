import requests
import chromadb


OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "nomic-embed-text:latest"

DOCUMENT = (
    "Patient presents with chest pain and shortness of breath. "
    "ECG evaluation and cardiac assessment are recommended."
)


def create_embedding(text: str) -> list[float]:
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
        raise RuntimeError("Ollama returned no embeddings")

    return embeddings[0]


def main() -> None:
    embedding = create_embedding(DOCUMENT)

    print(f"Embedding dimension: {len(embedding)}")

    client = chromadb.HttpClient(
        host="localhost",
        port=8004,
    )

    collection = client.get_or_create_collection(
        name="medical_documents"
    )

    collection.upsert(
        ids=["3"],
        documents=[DOCUMENT],
        embeddings=[embedding],
        metadatas=[
            {
                "case_id": "4",
                "filename": "cardiology_test.txt",
                "document_type": "medical_report",
            }
        ],
    )

    print("Chroma test data seeded successfully.")


if __name__ == "__main__":
    main()
