
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def split_documents(
    documents: list[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[Document]:
    """
    Split extracted PDF pages into smaller text chunks.

    Original metadata such as source filename and page number
    is preserved in every chunk.
    """

    if not documents:
        raise ValueError("No documents provided for splitting.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("Chunk overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
        add_start_index=True,
    )

    chunks = splitter.split_documents(documents)

    # Give each chunk a unique index for easier debugging.
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = index

    return chunks
