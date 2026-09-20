import chromadb
from sentence_transformers import SentenceTransformer
from app.core.config import settings

# Load the embedding model once at import time
embedding_model = SentenceTransformer(settings.embedding_model)

# Connect to the persisted ChromaDB vector store
chroma_client = chromadb.PersistentClient(path=settings.vector_store_path)
collection = chroma_client.get_or_create_collection(name=settings.collection_name)


def retrieve_chunks(query: str, n_results: int = 3):
    """Retrieve the most relevant chunks for a given query."""
    query_embedding = embedding_model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    retrieved = []
    for i in range(len(results["ids"][0])):
        retrieved.append({
            "text": results["documents"][0][i],
            "domain": results["metadatas"][0][i]["domain"],
            "source": results["metadatas"][0][i]["source_file"],
            "distance": results["distances"][0][i]
        })
    return retrieved