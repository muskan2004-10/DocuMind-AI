
import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5000/api";

function App() {
  const fileInputRef = useRef(null);

  const [selectedFiles, setSelectedFiles] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");
  const [restoring, setRestoring] = useState(true);

  useEffect(() => {
    async function restoreSession() {
      const savedSessionId = localStorage.getItem("documind_session_id");

      if (!savedSessionId) {
        setRestoring(false);
        return;
      }

      try {
        const response = await fetch(
          `${API_URL}/chat/history/${savedSessionId}`
        );

        const data = await response.json();

        if (!response.ok) {
          localStorage.removeItem("documind_session_id");
          setRestoring(false);
          return;
        }

        setSessionId(savedSessionId);
        setMessages(data.messages || []);
        setDocuments(data.documents || []);

      } catch (err) {
        setError("Could not restore your previous conversation.");
      } finally {
        setRestoring(false);
      }
    }

    restoreSession();
  }, []);

  function handleFileChange(event) {
    const files = Array.from(event.target.files || []);
    const pdfs = files.filter((file) => file.type === "application/pdf");

    if (pdfs.length !== files.length) {
      setError("Only PDF files are supported.");
    } else {
      setError("");
    }

    setSelectedFiles(pdfs);
  }

  async function handleUpload() {
    if (!selectedFiles.length) {
      setError("Please select at least one PDF.");
      return;
    }

    setUploading(true);
    setError("");

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Upload failed.");
      }

      setSessionId(data.session_id);

      localStorage.setItem(
        "documind_session_id",
        data.session_id
      );

      setDocuments(selectedFiles.map((file) => file.name));
      setMessages([
        {
          role: "assistant",
          content: `Successfully processed ${data.files_uploaded} PDF(s). I created ${data.chunks_created} searchable text chunks. Ask me anything about your documents.`,
        },
      ]);
      setSelectedFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      setError(err.message || "Could not connect to the backend.");
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk(event) {
    event.preventDefault();

    if (!question.trim() || !sessionId || asking) return;

    const currentQuestion = question.trim();

    setMessages((previous) => [
      ...previous,
      { role: "user", content: currentQuestion },
    ]);
    setQuestion("");
    setAsking(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          question: currentQuestion,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Could not generate an answer.");
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      setError(err.message || "Could not connect to the backend.");
    } finally {
      setAsking(false);
    }
  }

  if (restoring) {
    return (
      <div className="app-shell">
        <div className="empty-chat">
          Restoring your previous conversation...
        </div>
      </div>
    );
  }
  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark">D</span>
          <span>DocuMind<span className="brand-light"> AI</span></span>
        </a>
        <span className="topbar-label">MULTI-DOCUMENT INTELLIGENCE</span>
        <span className={`status ${sessionId ? "status-ready" : ""}`}>
          <span className="status-dot" />
          {sessionId ? "Documents ready" : "Ready to start"}
        </span>
      </header>

      <main className="main-layout">
        <section className="intro">
          <p className="eyebrow">YOUR DOCUMENTS, UNDERSTOOD</p>
          <h1>Ask your documents<br /><span>anything.</span></h1>
          <p className="intro-copy">
            Upload your PDFs and have a conversation with the information
            inside them. Get answers grounded in your documents.
          </p>
        </section>

        <section className="workspace">
          <aside className="sidebar">
            <div className="panel-heading">
              <div>
                <p className="section-label">WORKSPACE</p>
                <h2>Your documents</h2>
              </div>
              <span className="file-count">{documents.length}</span>
            </div>

            <div
              className="upload-zone"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                event.preventDefault();
                const files = Array.from(event.dataTransfer.files);
                setSelectedFiles(
                  files.filter((file) => file.type === "application/pdf")
                );
                setError("");
              }}
              role="button"
              tabIndex={0}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  fileInputRef.current?.click();
                }
              }}
            >
              <div className="upload-icon">↑</div>
              <strong>Drop PDFs here</strong>
              <span>or click to browse files</span>
              <small>PDF only · Maximum 10 files</small>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,application/pdf"
                multiple
                hidden
                onChange={handleFileChange}
              />
            </div>

            {selectedFiles.length > 0 && (
              <div className="selected-files">
                <p className="section-label">SELECTED TO UPLOAD</p>
                {selectedFiles.map((file, index) => (
                  <div className="file-row" key={`${file.name}-${index}`}>
                    <span className="pdf-icon">PDF</span>
                    <span className="file-name">{file.name}</span>
                    <button
                      className="remove-file"
                      onClick={() =>
                        setSelectedFiles((previous) =>
                          previous.filter((_, i) => i !== index)
                        )
                      }
                      aria-label={`Remove ${file.name}`}
                    >
                      ×
                    </button>
                  </div>
                ))}

                <button
                  className="upload-button"
                  onClick={handleUpload}
                  disabled={uploading}
                >
                  {uploading ? "Processing documents..." : "Upload and process"}
                </button>
              </div>
            )}

            {documents.length > 0 && (
              <div className="document-list">
                <p className="section-label">PROCESSED DOCUMENTS</p>
                {documents.map((name, index) => (
                  <div className="file-row" key={`${name}-${index}`}>
                    <span className="pdf-icon">PDF</span>
                    <span className="file-name">{name}</span>
                    <span className="check-icon">✓</span>
                  </div>
                ))}
              </div>
            )}

            <div className="sidebar-note">
              <span>✦</span>
              <p>Your documents are processed into searchable chunks to help retrieve relevant information.</p>
            </div>
          </aside>

          <section className="chat-panel">
            <div className="chat-header">
              <div>
                <p className="section-label">AI ASSISTANT</p>
                <h2>Document chat</h2>
              </div>
              <span className="model-tag">GROQ · RAG</span>
            </div>

            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="empty-chat">
                  <div className="empty-chat-icon">✳</div>
                  <h3>Your conversation starts here.</h3>
                  <p>
                    Upload one or more PDFs to start asking questions.
                    I'll search their contents and generate answers based
                    on the information I find.
                  </p>
                  <div className="suggestion">
                    <span>TRY ASKING</span>
                    "Summarize the key points in my documents."
                  </div>
                </div>
              ) : (
                messages.map((message, index) => (
                  <article className={`message ${message.role}`} key={index}>
                    <div className="message-avatar">
                      {message.role === "assistant" ? "D" : "Y"}
                    </div>
                    <div className="message-body">
                      <span className="message-role">
                        {message.role === "assistant" ? "DOCUMIND AI" : "YOU"}
                      </span>
                      <p>{message.content}</p>

                      {message.sources?.length > 0 && (
                        <div className="sources">
                          <span className="sources-heading">SOURCES</span>
                          {message.sources.map((source, sourceIndex) => (
                            <details className="source-item" key={sourceIndex}>
                              <summary>
                                {source.source} · Page {source.page}
                              </summary>
                              <p>{source.content}</p>
                            </details>
                          ))}
                        </div>
                      )}
                    </div>
                  </article>
                ))
              )}

              {asking && (
                <div className="thinking">
                  <span className="thinking-dot" />
                  Searching your documents and generating an answer...
                </div>
              )}
            </div>

            <form className="chat-input-area" onSubmit={handleAsk}>
              {!sessionId && (
                <p className="input-hint">Upload PDFs before asking a question.</p>
              )}
              <div className="chat-input-wrap">
                <input
                  type="text"
                  placeholder={
                    sessionId
                      ? "Ask a question about your documents..."
                      : "Upload documents to begin..."
                  }
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  disabled={!sessionId || asking}
                />
                <button
                  type="submit"
                  disabled={!sessionId || !question.trim() || asking}
                  aria-label="Send question"
                >
                  ↑
                </button>
              </div>
              <p className="disclaimer">
                AI-generated responses can be inaccurate. Check the cited sources.
              </p>
            </form>
          </section>
        </section>

        {error && (
          <div className="error-message" role="alert">
            {error}
            <button onClick={() => setError("")}>×</button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
