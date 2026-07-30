from app.services.embedding_services import EmbeddingService
from app.services.vector_store import VectorStore


embedding_service = EmbeddingService()


texts = [
    "Article 21 protects the right to life and personal liberty.",
    "Fundamental Rights are guaranteed by the Constitution of India.",
    "A contract is an agreement enforceable by law."
]


embeddings = embedding_service.create_embeddings(texts)


vector_store = VectorStore(
    dimension=384
)


vector_store.add_embeddings(
    embeddings,
    texts
)


query = "What is the right to life?"


query_embedding = embedding_service.create_embeddings(
    [query]
)[0]


results = vector_store.search(
    query_embedding,
    top_k=2
)


print("Search Results:")

for result in results:

    print("\n", result)