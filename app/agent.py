import ast
import operator
import sqlite3
import time

import faiss
import numpy as np
import requests

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings


# ============================================================
# INPUT GUARDRAIL
# ============================================================

def validate_user_input(user_input: str) -> str | None:
    """Return an error message if the input is invalid, otherwise None."""
    if not user_input.strip():
        return "Input cannot be empty."

    if len(user_input) > 500:
        return "Input is too long. Please keep your question under 500 characters."

    suspicious_patterns = [
        "__import__",
        "import os",
        "import sys",
        "subprocess",
        "os.system",
        "eval(",
        "exec(",
        "open(",
    ]

    lowered_input = user_input.lower()

    for pattern in suspicious_patterns:
        if pattern in lowered_input:
            return (
                "Input rejected because it contains potentially unsafe "
                "code or commands."
            )

    return None


# ============================================================
# OUTPUT GUARDRAIL
# ============================================================

def validate_agent_output(output: str) -> str:
    """Validate the agent's final answer before showing it to the user."""

    if not output or not output.strip():
        return (
            "I could not provide a reliable answer because "
            "the agent did not produce a valid response."
        )

    suspicious_patterns = [
        "555-",
        "@company.com",
    ]

    for pattern in suspicious_patterns:
        if pattern.lower() in output.lower():
            return (
                "I could not provide a reliable answer because "
                "the agent produced information that could not be verified."
            )

    return output


# ============================================================
# SQL DATABASE TOOL
# ============================================================

@tool
def query_customers(sql_query: str) -> str:
    """Query the customers SQLite database using a SELECT statement.

    Always provide a complete valid SQL query.
    When filtering by city, put the city name in single quotes.
    Example:
    SELECT COUNT(*) FROM customers WHERE city = 'Munich'
    """

    try:
        connection = sqlite3.connect("data/customers.db")
        cursor = connection.cursor()

        query = sql_query.strip().lower()

        if not query.startswith("select"):
            connection.close()
            return "Only SELECT queries are allowed."

        cursor.execute(sql_query)

        result = cursor.fetchall()

        connection.close()

        return str(result)

    except sqlite3.Error as e:
        return f"SQL error: {e}"


# ============================================================
# WEATHER API TOOL
# ============================================================

@tool
def get_weather(latitude: float, longitude: float) -> str:
    """Get the current weather for a latitude and longitude."""

    url = url = url = url = url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m",
    }

    for attempt in range(3):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            temperature = data["current"]["temperature_2m"]
            wind_speed = data["current"]["wind_speed_10m"]

            return (
                f"Current temperature: {temperature}°C\n"
                f"Wind speed: {wind_speed} km/h"
            )

        except requests.HTTPError as e:
            print(f"Weather API HTTP error: {e}")

            if response.status_code < 500:
                return f"Weather API request was rejected: {e}"

            if attempt == 2:
                return f"Weather API failed after 3 attempts: {e}"

        except requests.Timeout as e:
            print(
                f"Weather API timeout on attempt "
                f"{attempt + 1}: {e}"
            )

            if attempt == 2:
                return f"Weather API failed after 3 attempts: {e}"

            time.sleep(2)
        except requests.RequestException as e:
            print(
                f"Weather API request failed on attempt "
                f"{attempt + 1}: {e}"
            )

            if attempt == 2:
                return f"Weather API failed after 3 attempts: {e}"
            time.sleep(2)

        except (KeyError, TypeError, ValueError) as e:
            return f"Weather API returned unexpected data: {e}"

    return "Weather API failed unexpectedly."


# ============================================================
# KNOWLEDGE BASE / RETRIEVER
# ============================================================

with open("data/knowledge.txt", "r", encoding="utf-8") as file:
    documents = [
        paragraph.strip()
        for paragraph in file.read().split("\n\n")
        if paragraph.strip()
    ]


embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

document_vectors = embeddings.embed_documents(documents)

document_vectors = np.array(
    document_vectors,
    dtype="float32"
)

dimension = document_vectors.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(document_vectors)


@tool
def search_knowledge_base(question: str) -> str:
    """Search the company knowledge base for relevant information."""

    try:
        query_vector = embeddings.embed_query(question)

        query_vector = np.array(
            [query_vector],
            dtype="float32"
        )

        distances, indices = index.search(
            query_vector,
            k=2
        )

        if len(indices[0]) == 0:
            return "No relevant information found."

        return "\n".join(
            documents[index_number]
            for index_number in indices[0]
        )

    except Exception as e:
        return f"Retriever error: {e}"


# ============================================================
# CALCULATOR TOOL
# ============================================================

import ast
import operator


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_calculate(expression: str) -> float | int:
    """Safely evaluate a basic mathematical expression."""

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(
            node.value, (int, float)
        ):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)
            return ALLOWED_OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
            operand = evaluate(node.operand)
            return ALLOWED_OPERATORS[type(node.op)](operand)

        raise ValueError("Unsupported expression.")

    return evaluate(tree.body)


@tool
def calculator(expression: str) -> str:
    """Calculate a basic mathematical expression safely."""

    try:
        result = safe_calculate(expression)
        return str(result)

    except Exception:
        return "Could not calculate the expression."


# ============================================================
# LOCAL LLM
# ============================================================

llm = ChatOllama(
    model="llama3.1",
    temperature=0,
    num_predict=256,
)


# ============================================================
# AGENT
# ============================================================

agent = create_agent(
    model=llm,
    tools=[
        calculator,
        query_customers,
        get_weather,
        search_knowledge_base,
    ],
   system_prompt=(
    "You are a helpful tool-using assistant. "
    "Use a tool only when necessary to answer the user's question. "
    "For customer questions, use query_customers to retrieve the answer from the database. "
    "If the user provides a city name, do not ask for it again; execute the database query. "
    "For knowledge base questions, call search_knowledge_base at most once. "
    "After receiving a result from search_knowledge_base, use that result "
    "to answer the user immediately. "
    "Do not call the same tool repeatedly for the same question. "
    "Always include the actual facts returned by the tool in your answer. "
    "Do not describe weather API results as coming from the database. "
    "Describe weather results as coming from the weather API. "
    "Always include the actual temperature and wind speed returned by the weather API. "
    "Describe customer results as coming from the customer database. "
    "Describe knowledge results as coming from the knowledge base. "
    "If the tools do not provide enough information, clearly say so and "
    "do not invent facts."
),
)