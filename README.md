# DocuMind AI – Intelligent Multi-Document Question Answering System

DocuMind AI is an AI-powered document question-answering application that allows users to upload multiple PDF documents and interact with them through natural-language conversations.

Built using **Retrieval-Augmented Generation (RAG)**, it retrieves relevant information from uploaded documents and uses a Large Language Model (LLM) to generate contextual answers with source references.

Instead of manually searching through lengthy documents, users can ask questions and receive answers grounded in the content of their uploaded PDFs.

## Features

- **Multi-PDF Upload:** Upload and process multiple PDF documents in one session.
- **PDF Text Extraction:** Extract text and page-level metadata from PDF files.
- **Text Chunking:** Split extracted text into smaller, overlapping chunks for better retrieval.
- **Semantic Search:** Retrieve relevant information based on meaning rather than exact keyword matches.
- **Vector Database:** Generate and store document embeddings using FAISS.
- **AI-Powered Answers:** Generate contextual responses using a Groq-hosted LLM.
- **Source References:** Display relevant document filenames and page numbers with answers.
- **Conversational Interface:** Ask follow-up questions using previous conversation context.
- **Persistent Chat History:** Store conversations in SQLite and restore them when the user refreshes the browser.
- **Session-Based Storage:** Maintain separate document indexes and conversations for individual upload sessions.
- **Grounded Responses:** Instruct the LLM to base its answers on retrieved document content and avoid presenting unsupported information as fact.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | React.js, JavaScript, Vite |
| Backend | Python, Flask |
| AI Framework | LangChain |
| LLM Provider | Groq |
| Language Model | GPT-OSS 20B |
| Embedding Model | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Database | FAISS |
| PDF Processing | PyMuPDF |
| Conversation Storage | SQLite |
| Environment Variables | python-dotenv |
| API Communication | REST API |

## Architecture

### Document Processing and Indexing

```text
User uploads PDF files
        |
        v
   React Frontend
        |
        v
     Flask API
        |
        v
   PDF Text Extraction
        |
        v
     Text Chunking
        |
        v
 HuggingFace Embeddings
        |
        v
   FAISS Vector Store
```

### Question Answering

```text
User asks a question
        |
        v
   Flask API
        |
        v
  Question Rewriting
        |
        v
 Semantic Retrieval (FAISS)
        |
        v
 Relevant Document Chunks
        |
        v
     Groq LLM
        |
        v
 Contextual Answer + Sources
        |
        v
   React Frontend
        |
        v
  SQLite Chat History
```

## Project Structure

```text
DocuMind-AI/
│
├── backend/
│   ├── app.py
│   ├── chat_history.py
│   ├── requirements.txt
│   │
│   ├── rag/
│   │   ├── document_loader.py
│   │   ├── text_splitter.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   └── generator.py
│   │
│   ├── uploads/
│   ├── vector_db/
│   └── test_*.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── sample_documents/
├── .env.example
├── .gitignore
└── README.md
```

Generated files such as uploaded PDFs, FAISS indexes, and the SQLite database are stored locally and should not be committed to Git.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/muskan2004-10/DocuMind-AI.git

cd DocuMind-AI
```

### 2. Set up the Python backend

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```bash
python -m pip install -r backend/requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Get your Groq API key from:

https://console.groq.com/keys

The Hugging Face embedding model can be downloaded without an access token for normal use. If you configure an optional Hugging Face token, keep it private as well.

**Never commit your actual `.env` file or API keys to GitHub.**

### 4. Start the backend

From the project root:

```bash
python backend/app.py
```

Backend URL:

```text
http://127.0.0.1:5000
```

Health check:

```text
http://127.0.0.1:5000/api/health
```

### 5. Start the frontend

Open another terminal:

```powershell
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed in your terminal, typically:

http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check backend status |
| POST | `/api/upload` | Upload and index PDF documents |
| POST | `/api/chat` | Ask questions about uploaded documents |
| GET | `/api/chat/history/<session_id>` | Restore a conversation and its document list |

### Upload Documents

**Endpoint:** `POST /api/upload`

Accepts multiple PDF files using multipart form data with the field name `files`.

Returns session information and document-processing statistics.

### Ask Questions

**Endpoint:** `POST /api/chat`

Example request:

```json
{
  "session_id": "your-session-uuid",
  "question": "Summarize the uploaded document."
}
```

Returns an AI-generated answer and relevant source references.

### Restore Chat History

**Endpoint:** `GET /api/chat/history/<session_id>`

Retrieves the saved messages and document list associated with a session.

## How RAG Works

DocuMind AI follows a Retrieval-Augmented Generation pipeline:

1. **Document Loading:** Extract text and page metadata from uploaded PDF files.
2. **Chunking:** Divide extracted text into smaller, overlapping sections.
3. **Embedding Generation:** Convert text chunks into numerical vector representations using Sentence Transformers.
4. **Vector Storage:** Store the embeddings in a FAISS vector database.
5. **Question Rewriting:** Use conversation history to make follow-up questions understandable as standalone queries.
6. **Retrieval:** Search the vector database for document chunks relevant to the question.
7. **Generation:** Pass the retrieved context to the Groq-hosted LLM.
8. **Response:** Generate an answer with relevant document references.
9. **History Storage:** Save user questions and assistant responses in SQLite for later restoration.

## Current Limitations

- Scanned PDFs that contain images instead of extractable text are not supported because OCR has not been implemented.
- Conversation restoration currently relies on the browser's saved session ID and the backend's local files.
- The application does not yet provide user authentication or a multi-conversation management interface.
- Previously generated source details are not currently guaranteed to be restored with old chat messages.
- The current setup is intended as a working project MVP, not a production-scale deployment.

## Future Improvements

- OCR support for scanned PDFs.
- User authentication and document management.
- Multiple conversation management.
- Persistent storage suitable for cloud deployment.
- Improved source citation and retrieval evaluation.
- Better handling of large documents and concurrent users.

## Project Status

**Working MVP:** PDF upload, document indexing, semantic retrieval, LLM-based question answering, source references, and SQLite-backed conversation history have been implemented and tested locally.

## Author

**Muskan Atray**

- GitHub: https://github.com/muskan2004-10

---

*DocuMind AI – Making documents easier to understand through AI.*