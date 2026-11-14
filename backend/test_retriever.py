
from rag.embeddings import get_embedding_model
from rag.vector_store import load_vector_store
from rag.retriever import retrieve_documents


# Load the embedding model
embedding_model = get_embedding_model()

# Load the previously saved vector database
vector_store = load_vector_store(embedding_model)

# Ask a question
query = "What technical projects have I worked on?"

# Retrieve relevant chunks
results = retrieve_documents(
    vector_store=vector_store,
    query=query,
    k=4
)

# Display results
print("\nRetrieved Documents:\n")

for index, result in enumerate(results, start=1):
    print(f"Result: {index}")
    print(f"Source: {result['source']}")
    print(f"Page: {result['page']}")
    print(f"Distance Score: {result['score']:.4f}")
    print(f"Content: {result['content']}")
    print("-" * 50)
