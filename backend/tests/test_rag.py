from app.tools.rag_tool import search_medical_documents


def test_rag_search_filters_by_case_id():
    result = search_medical_documents(
        query="Patient reports chest pain and shortness of breath.",
        limit=3,
        case_id=4,
    )

    assert result["ids"]
    assert result["documents"]
    assert result["metadatas"]

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]

    assert len(documents) == 1
    assert metadatas[0]["case_id"] == "4"
    assert metadatas[0]["filename"] == "cardiology_test.txt"
