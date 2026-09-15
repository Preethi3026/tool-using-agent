import faiss
import numpy as np

from langchain_ollama import OllamaEmbeddings


# Load the knowledge base
with open("data/knowledge.txt", "r", encoding="utf-8") as file:
    text = file.read()

documents = [
    part.strip()
    for part in text.split("\n\n")
    if part.strip()
]


# Create the embedding model
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)


# Create embeddings for all documents
document_vectors = embeddings.embed_documents(documents)

document_vectors = np.array(
    document_vectors,
    dtype="float32"
)


# Create FAISS index
dimension = document_vectors.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(document_vectors)


# Search the knowledge base
question = "What are the customer support hours?"

query_vector = embeddings.embed_query(question)

query_vector = np.array(
    [query_vector],
    dtype="float32"
)


distances, indices = index.search(
    query_vector,
    k=2
)


print("Most relevant information:")

for index_number in indices[0]:
    print("-", documents[index_number])