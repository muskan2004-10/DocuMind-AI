
from pathlib import Path

from rag.document_loader import load_multiple_pdfs
from rag.text_splitter import split_documents


# Step 1: Find sample PDFs
pdf_files = list(Path("sample_documents").glob("*.pdf"))

if not pdf_files:
    print("No PDFs found. Add PDFs to sample_documents first.")
    raise SystemExit(1)


# Step 2: Extract PDF text
documents = load_multiple_pdfs(
    [str(file) for file in pdf_files]
)

print("Original pages:", len(documents))


# Step 3: Split extracted text into chunks
chunks = split_documents(
    documents,
    chunk_size=800,
    chunk_overlap=150,
)

print("Total chunks:", len(chunks))


# Step 4: Inspect the first few chunks
for chunk in chunks[:5]:
    print("\n-----------------------------")
    print("Chunk index:", chunk.metadata["chunk_index"])
    print("Source:", chunk.metadata["source"])
    print("Page:", chunk.metadata["page"])
    print("Start index:", chunk.metadata["start_index"])
    print("Chunk length:", len(chunk.page_content))
    print("Text preview:", chunk.page_content[:200])
