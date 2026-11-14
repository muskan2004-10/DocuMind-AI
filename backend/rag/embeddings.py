
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Load a local HuggingFace embedding model.
    """

    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def embed_documents(
    documents: list[Document],
    embedding_model: HuggingFaceEmbeddings,
) -> list[list[float]]:
    """
    Convert document chunks into numerical vectors.
    """

    if not documents:
        raise ValueError("No documents provided for embedding.")

    texts = [document.page_content for document in documents]

    vectors = embedding_model.embed_documents(texts)

    return vectors


def embed_query(
    query: str,
    embedding_model: HuggingFaceEmbeddings,
) -> list[float]:
    """
    Convert a user's question into a numerical vector.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    return embedding_model.embed_query(query)
