from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

vector = embeddings.embed_query(
    "What are the customer support hours?"
)

print("Embedding created successfully!")
print("Vector length:", len(vector))