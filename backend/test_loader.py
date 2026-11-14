
from pathlib import Path

from rag.document_loader import load_multiple_pdfs


# Find all PDFs in the sample_documents folder
pdf_files = list(Path("sample_documents").glob("*.pdf"))

if not pdf_files:
    print("No PDF files found. Add a PDF to sample_documents first.")
else:
    documents = load_multiple_pdfs(
        [str(file) for file in pdf_files]
    )

    print(f"\nTotal pages extracted: {len(documents)}")

    for document in documents:
        print("\n-----------------------------")
        print("Source:", document.metadata["source"])
        print("Page:", document.metadata["page"])
        print("Text preview:", document.page_content[:300])
