# DocuMind AI – Intelligent Document Question Answering System

DocuMind AI is an AI-powered document question-answering application that allows users to upload PDF documents and interact with them through natural language conversations.

Built using Retrieval-Augmented Generation (RAG), it retrieves relevant information from uploaded documents and generates contextual answers using a Large Language Model (LLM).

Instead of manually searching through lengthy documents, users can simply ask questions and receive relevant answers with source references.

## Features

- **Multi-PDF Upload:** Upload and process multiple PDF documents in one session.
- **Intelligent Document Processing:** Extract text from PDFs and split it into smaller, overlapping chunks.
- **Semantic Search:** Find relevant document information based on meaning rather than exact keyword matches.
- **Vector Database:** Store and retrieve document embeddings using FAISS.
- **AI-Powered Answers:** Generate contextual responses using Groq-hosted LLMs.
- **Source References:** Display document filenames and page numbers alongside answers.
- **Conversational Interface:** Ask follow-up questions about uploaded documents.
- **Session-Based Storage:** Maintain separate document indexes for individual upload sessions.
- **Context-Aware Responses:** Distinguish hypothetical examples from verified document information.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | React.js, TypeScript, Vite |
| Backend | Python, Flask |
| AI Framework | LangChain |
| LLM Provider | Groq |
| Language Model | GPT-OSS 20B |
| Embedding Model | HuggingFace Sentence Transformers |
| Vector Database | FAISS |
| PDF Processing | PyMuPDF |
| Environment Management | Python dotenv |
| API Communication | REST API |

## Architecture

```text
             USER
               |
               v
       React Frontend
               |
               v
          Flask API
               |
       PDF Upload & Processing
               |
               v
        Text Extraction
               |
               v
          Text Chunking
               |
               v
       HuggingFace Embeddings
               |
               v
         FAISS Vector DB
               |
               v
        Semantic Retrieval
               |
               v
          Groq LLM
               |
               v
       Contextual Answer
               |
               v
       Source References
               |
               v
        React Frontend
```

## Project Structure

```text
DocuMind-AI/
│
├── backend/
│   ├── app.py
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
│   │
│   └── test_*.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── .gitignore
├── .env.example
└── README.md
```

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

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
```

Get your Groq API key from:

https://console.groq.com/keys

The Hugging Face token is optional for basic model downloads, but can help with authenticated Hub access.

**Never commit your actual `.env` file to GitHub.**

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

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed in your terminal, typically:

```text
http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check backend status |
| POST | `/api/upload` | Upload and index PDF documents |
| POST | `/api/chat` | Ask questions about uploaded documents |

### Upload Documents

Endpoint:

```text
POST /api/upload
```

Accepts multiple PDF files using multipart form data with the field name `files`.

Returns session information, processed page count and created chunk count.

### Ask Questions

Endpoint:

```text
POST /api/chat
```

Example request:

```json
{
  "session_id": "your-session-uuid",
  "question": "Summarize the uploaded document."
}
```

Returns an AI-generated answer and relevant source references.

## How RAG Works

DocuMind AI follows a Retrieval-Augmented Generation pipeline:

1. **Document Loading:** Extract text and metadata from uploaded PDF files.
2. **Chunking:** Split extracted text into smaller overlapping sections.
3. **Embedding Generation:** Convert text chunks into numerical vector representations.
4. **Vector Storage:** Store embeddings in a FAISS vector database.
5. **Retrieval:** Find the most relevant chunks for a user's question.
6. **Generation:** Pass retrieved context to the Groq LLM.
7. **Response:** Generate an answer with relevant document references.

## Future Improvements

- Persistent conversation history using SQLite.
- Improved multi-turn conversational memory.
- Support for scanned PDFs through OCR.
- User authentication and document management.
- More advanced source citation and relevance evaluation.
- Cloud deployment and production optimization.

## Project Status

Currently under active development.

## Author

**Muskan Atray**

- GitHub: https://github.com/muskan2004-10

---

*DocuMind AI – Making documents easier to understand through AI.*