
from langchain_core.documents import Document


def retrieve_documents(vector_store, query: str, k: int = 4):
    """
    Retrieve the k most relevant document chunks for a query.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if k < 1:
        raise ValueError("k must be at least 1.")

    results = vector_store.similarity_search_with_score(
        query,
        k=k
    )

    retrieved_documents = []

    for document, score in results:
        retrieved_documents.append({
            "content": document.page_content,
            "source": document.metadata.get("source", "Unknown"),
            "page": document.metadata.get("page", "Unknown"),
            "score": float(score)
        })

    return retrieved_documents
