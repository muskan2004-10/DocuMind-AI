
import os
import uuid
import logging

from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from rag.document_loader import load_multiple_pdfs
from rag.text_splitter import split_documents
from rag.embeddings import get_embedding_model
from rag.vector_store import create_vector_store, save_vector_store
from rag.vector_store import load_vector_store
from rag.retriever import retrieve_documents
from rag.generator import generate_answer, rewrite_question
from chat_history import (
    init_db,
    create_conversation,
    save_message,
    get_chat_history,
    conversation_exists
)
# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env")

UPLOAD_FOLDER = BACKEND_DIR / "uploads"
VECTOR_DB_FOLDER = BACKEND_DIR / "vector_db"

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
VECTOR_DB_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILES = 10

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {"origins": "http://localhost:5173"}
})

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

logging.basicConfig(level=logging.INFO)

# Initialise SQLite chat-history tables.
init_db()
# Load the embedding model only once.
embedding_model = None


def get_model():
    global embedding_model

    if embedding_model is None:
        embedding_model = get_embedding_model()

    return embedding_model


# --------------------------------------------------
# 2. Helper functions
# --------------------------------------------------

def is_valid_session_id(session_id):
    try:
        uuid.UUID(session_id)
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def get_session_vector_path(session_id):
    return VECTOR_DB_FOLDER / session_id


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# --------------------------------------------------
# 3. Health check
# --------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "success",
        "message": "DocuMind AI backend is running."
    }), 200


# --------------------------------------------------
# 4. Upload and index multiple PDFs
# --------------------------------------------------

@app.route("/api/upload", methods=["POST"])
def upload_documents():

    files = request.files.getlist("files")

    if not files or not files[0].filename:
        return jsonify({
            "error": "Please select at least one PDF."
        }), 400

    if len(files) > MAX_FILES:
        return jsonify({
            "error": f"You can upload a maximum of {MAX_FILES} PDFs."
        }), 400

    for file in files:
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Only PDF files are supported."
            }), 400

    # Create an isolated session for this upload.
    session_id = str(uuid.uuid4())

    session_upload_folder = UPLOAD_FOLDER / session_id
    session_upload_folder.mkdir(parents=True, exist_ok=True)

    saved_file_paths = []

    try:
        # Save uploaded PDFs.
        for file in files:
            original_name = secure_filename(file.filename)

            unique_name = f"{uuid.uuid4().hex}_{original_name}"
            file_path = session_upload_folder / unique_name

            file.save(str(file_path))
            saved_file_paths.append(str(file_path))

        # Extract PDF text.
        documents = load_multiple_pdfs(saved_file_paths)

        if not documents:
            return jsonify({
                "error": "No readable text found in the uploaded PDFs."
            }), 400

        # Split text into chunks.
        chunks = split_documents(documents)

        # Generate embeddings and create FAISS index.
        model = get_model()

        vector_store = create_vector_store(
            chunks=chunks,
            embedding_model=model
        )

        # Save this session's vector database.
        vector_path = get_session_vector_path(session_id)

        save_vector_store(
            vector_store=vector_store,
            storage_path=vector_path
        )
        # Create a database conversation for this document session.
        create_conversation(session_id)

        return jsonify({
            "status": "success",
            "message": "Documents uploaded and indexed successfully.",
            "session_id": session_id,
            "files_uploaded": len(files),
            "pages_processed": len(documents),
            "chunks_created": len(chunks)
        }), 200

    except Exception as error:
        logging.exception("Document upload failed")

        return jsonify({
            "error": str(error)
        }), 500


# --------------------------------------------------
# 5. Retrieve previous chat history
# --------------------------------------------------

@app.route("/api/chat/history/<session_id>", methods=["GET"])
def restore_chat_history(session_id):

    if not is_valid_session_id(session_id):
        return jsonify({
            "error": "Invalid session ID."
        }), 400

    if not conversation_exists(session_id):
        return jsonify({
            "error": "Conversation not found."
        }), 404

    vector_path = get_session_vector_path(session_id)

    if not (vector_path / "index.faiss").exists():
        return jsonify({
            "error": "Documents for this conversation are unavailable."
        }), 404

    history = get_chat_history(session_id)

    # Restore original document filenames.
    session_folder = UPLOAD_FOLDER / session_id

    documents = []

    if session_folder.exists():
        for file_path in session_folder.iterdir():
            if file_path.is_file():
                original_name = file_path.name.split("_", 1)[-1]
                documents.append(original_name)

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "messages": history,
        "documents": documents
    }), 200

# --------------------------------------------------
# 6. Ask questions about uploaded documents
# --------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    session_id = data.get("session_id")
    question = data.get("question", "")

    if not isinstance(question, str):
        return jsonify({"error": "Question must be text."}), 400

    question = question.strip()

    if not session_id or not is_valid_session_id(session_id):
        return jsonify({
            "error": "A valid session_id is required."
        }), 400

    if not question:
        return jsonify({
            "error": "Please enter a question."
        }), 400

    if not conversation_exists(session_id):
        return jsonify({
            "error": "Conversation not found. Upload PDFs first."
        }), 404

    vector_path = get_session_vector_path(session_id)

    if not (vector_path / "index.faiss").exists():
        return jsonify({
            "error": "No documents found for this session."
        }), 404

    try:
        # Retrieve trusted conversation history from SQLite.
        chat_history = get_chat_history(session_id)

        # Save the new user question.
        save_message(
            session_id=session_id,
            role="user",
            content=question,
            message_type="user_provided"
        )

        # Load the session's vector database.
        model = get_model()

        vector_store = load_vector_store(
            embedding_model=model,
            storage_path=vector_path
        )

        # Rewrite follow-up questions using stored history.
        standalone_question = rewrite_question(
            question=question,
            chat_history=chat_history
        )

        # Retrieve relevant document chunks.
        documents = retrieve_documents(
            vector_store=vector_store,
            query=standalone_question,
            k=4
        )

        # Generate the answer using retrieved documents
        # and the previous conversation.
        answer = generate_answer(
            question=standalone_question,
            retrieved_documents=documents,
            chat_history=chat_history
        )

        # Save the assistant's answer.
        save_message(
            session_id=session_id,
            role="assistant",
            content=answer,
            message_type="unverified"
        )

        # Prepare source references.
        sources = []
        seen_sources = set()

        for doc in documents:
            source_key = (doc["source"], doc["page"])

            if source_key not in seen_sources:
                seen_sources.add(source_key)

                sources.append({
                    "source": doc["source"],
                    "page": doc["page"],
                    "content": doc["content"]
                })

        return jsonify({
            "status": "success",
            "question": question,
            "answer": answer,
            "sources": sources
        }), 200

    except Exception:
        logging.exception("Chat request failed")

        return jsonify({
            "error": "Could not generate an answer. Please try again."
        }), 500

# --------------------------------------------------
# 7. Start Flask server
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
