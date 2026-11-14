
from pathlib import Path

from rag.document_loader import load_multiple_pdfs
from rag.text_splitter import split_documents
from rag.embeddings import get_embedding_model
from rag.vector_store import (
    create_vector_store,
    save_vector_store,
    load_vector_store,
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
embedding_model = get_embedding_model()

# Step 4: Create FAISS database
print("\nCreating FAISS vector database...")

vector_store = create_vector_store(
    chunks,
    embedding_model,
)

# Step 5: Save database
save_vector_store(vector_store)

print("Vector database saved successfully!")


# Step 6: Load database again
print("\nLoading saved vector database...")

loaded_store = load_vector_store(embedding_model)

print("Vector database loaded successfully!")


# Step 7: Search using a question
query = "What technical projects have I worked on?"

results = loaded_store.similarity_search(
    query,
    k=3,
)

print("\nSearch query:", query)
print("\nTop 3 matching chunks:")

for index, document in enumerate(results, start=1):
    print("\n-----------------------------")
    print("Result:", index)
    print("Source:", document.metadata["source"])
    print("Page:", document.metadata["page"])
    print("Content:", document.page_content[:300])
