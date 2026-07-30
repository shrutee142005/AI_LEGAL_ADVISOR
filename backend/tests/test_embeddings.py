from app.services.embedding_services import EmbeddingService


embedding_service = EmbeddingService()


texts = [
    "Article 21 protects the right to life and personal liberty.",
    "The Constitution of India provides fundamental rights."
]


embeddings = embedding_service.create_embeddings(texts)


print("Number of embeddings:", len(embeddings))

print(
    "Embedding dimension:",
    len(embeddings[0])
)

print(
    "First embedding:",
    embeddings[0][:5]
)