
from pathlib import Path

import pymupdf
from langchain_core.documents import Document


def load_pdf(file_path: str) -> list[Document]:
    """
    Extract text from a PDF, one Document per non-empty page.

    Each Document contains:
    - page_content: extracted text
    - metadata: source filename and page number
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    documents = []

    try:
        with pymupdf.open(path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()

                # Skip pages that contain no extractable text.
                if not text:
                    continue

                document = Document(
                    page_content=text,
                    metadata={
                        "source": path.name,
                        "page": page_number,
                    },
                )

                documents.append(document)

    except pymupdf.FileDataError as error:
        raise ValueError(f"Could not read PDF: {path.name}") from error

    if not documents:
        raise ValueError(
            f"No extractable text found in {path.name}. "
            "The PDF may be empty or scanned."
        )

    return documents


def load_multiple_pdfs(file_paths: list[str]) -> list[Document]:
    """
    Load multiple PDFs and combine their extracted pages.
    """

    if not file_paths:
        raise ValueError("Please provide at least one PDF file.")

    all_documents = []

    for file_path in file_paths:
        documents = load_pdf(file_path)
        all_documents.extend(documents)

    return all_documents
