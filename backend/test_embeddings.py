
from pathlib import Path

from rag.document_loader import load_multiple_pdfs
from rag.text_splitter import split_documents
from rag.embeddings import (
    get_embedding_model,
    embed_documents,
    embed_query,
)


# Step 1: Load PDFs
pdf_files = list(Path("sample_documents").glob("*.pdf"))

if not pdf_files:
    raise SystemExit("No PDFs found in sample_documents.")

documents = load_multiple_pdfs(
    [str(file) for file in pdf_files]
)

# Step 2: Split documents
chunks = split_documents(documents)

print("Total chunks:", len(chunks))


# Step 3: Load embedding model
print("\nLoading embedding model...")
embedding_model = get_embedding_model()

# Step 4: Generate document embeddings
print("\nGenerating embeddings...")
vectors = embed_documents(chunks, embedding_model)

print("Total vectors:", len(vectors))
print("Vector dimensions:", len(vectors[0]))


# Step 5: Generate a question embedding
query = "What technical projects have I worked on?"

query_vector = embed_query(query, embedding_model)

print("\nQuery:", query)
print("Query vector dimensions:", len(query_vector))
print("First 5 values:", query_vector[:5])
