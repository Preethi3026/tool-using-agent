from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.1",
    temperature=0
)

response = llm.invoke("What is an AI agent? Answer in one sentence.")

print(response.content)