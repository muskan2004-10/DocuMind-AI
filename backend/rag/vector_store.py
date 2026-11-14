
from pathlib import Path
from langchain_community.vectorstores import FAISS

DEFAULT_VECTOR_DB_PATH = (
    Path(__file__).resolve().parent.parent / "vector_db"
)


def create_vector_store(chunks, embedding_model):
    if not chunks:
        raise ValueError("No document chunks provided.")

    print("Creating FAISS vector database...")

    return FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model
    )


def save_vector_store(vector_store, storage_path=None):
    path = Path(storage_path) if storage_path else DEFAULT_VECTOR_DB_PATH

    path.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(path))

    print(f"Vector database saved at: {path}")


def load_vector_store(embedding_model, storage_path=None):
    path = Path(storage_path) if storage_path else DEFAULT_VECTOR_DB_PATH

    if not (path / "index.faiss").exists():
        raise FileNotFoundError(
            f"No FAISS database found at: {path}"
        )

    vector_store = FAISS.load_local(
        str(path),
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )

    return vector_store
