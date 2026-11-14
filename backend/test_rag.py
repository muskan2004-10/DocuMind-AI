
from rag.embeddings import get_embedding_model
from rag.vector_store import load_vector_store
from rag.retriever import retrieve_documents
from rag.generator import generate_answer


# 1. Load embedding model
embedding_model = get_embedding_model()

# 2. Load saved vector database
vector_store = load_vector_store(embedding_model)

# 3. Ask a question
question = "What technical projects have I worked on?"

# 4. Retrieve relevant document chunks
documents = retrieve_documents(
    vector_store=vector_store,
    query=question,
    k=4
)

# 5. Generate an answer using Groq
answer = generate_answer(
    question=question,
    retrieved_documents=documents
)

print("\nQuestion:")
print(question)

print("\nDocuMind AI Answer:")
print(answer)

print("\nRetrieved Sources:")

for doc in documents:
    print(f"- {doc['source']}, Page {doc['page']}")
