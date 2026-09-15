# Agent with Tools and Observability

A tool-using AI agent built with LangChain, LangGraph, and a local Ollama LLM.

The agent can use multiple tools to answer questions, including customer database queries, weather information, knowledge-base retrieval, and safe calculations.

The project also includes input/output guardrails, error handling, retry logic, and Langfuse observability.

## Features

- Tool-using AI agent with LangChain and LangGraph
- Local LLM inference using Ollama
- Customer database queries using SQLite
- Weather lookup using the Open-Meteo API
- Semantic knowledge-base search using FAISS and local embeddings
- Safe calculator using AST-based expression validation
- Input guardrails for potentially unsafe requests
- Output guardrails for suspicious generated content
- Retry and error handling for external API failures
- Langfuse tracing for agent, model, and tool observability
- Failure analysis and intentional failure testing

## Architecture

The agent follows a tool-calling workflow:

User question
    |
    v
Input guardrail
    |
    v
LangGraph agent
    |
    +----> Customer database tool
    |
    +----> Weather API tool
    |
    +----> Knowledge-base retriever
    |
    +----> Safe calculator
    |
    v
Output guardrail
    |
    v
Final answer

Langfuse traces the agent workflow, model calls, and tool calls for observability.

## Tools

### Customer Database

Queries the SQLite customer database using SQL. The tool is designed to return controlled errors for invalid SQL rather than crashing the agent.

### Weather

Retrieves weather information from the Open-Meteo API. The tool includes retry logic for transient request and timeout failures and avoids retrying non-retryable HTTP errors.

### Knowledge Base

Uses FAISS with local nomic-embed-text embeddings to retrieve relevant information from the project knowledge base.

### Safe Calculator

Evaluates mathematical expressions using Python's AST module and an allowlist of supported operations, preventing arbitrary Python code execution.

## Guardrails and Observability

### Input Guardrail

User input is checked before the agent runs. Potentially unsafe patterns such as imports, subprocess execution, eval, exec, and file-opening operations are rejected.

### Output Guardrail

The final AI response is checked for suspicious patterns before it is displayed. If the output cannot be considered reliable, a controlled fallback message is returned.

### Observability

Langfuse is used to trace:

- LangGraph agent execution
- LLM calls through ChatOllama
- Tool calls
- Tool execution flow

This makes it possible to inspect how the agent reached its final answer and diagnose failures.

### Failure Testing

The project intentionally tested failure scenarios including:

- Weather API connection failures
- Malformed SQL
- Repeated knowledge-base retrieval
- Unsupported knowledge-base questions
- Invalid weather coordinates
- Unsafe calculator expressions
- Suspicious generated output

The results and improvements are documented in FAILURE_ANALYSIS.md.

## Installation and Setup

### Requirements

- Python 3.12+
- Ollama
- llama3.1 model
- nomic-embed-text model
- Langfuse account for observability

### Environment Variables

The project uses an existing .env file for Langfuse configuration.

Keep .env private and do not commit your credentials to a public repository.



## Running the Agent

Make sure Ollama is running and the required models are available.

From the project root, run:

    python .\app\run_agent.py

The application will prompt you for a question. The agent will decide whether to use one of its available tools.

## Testing

The project was tested for both normal operation and failure handling.

- Customer database queries returned expected results.
- Knowledge-base retrieval returned relevant information.
- Weather API requests returned temperature and wind information.
- Weather connection failures were retried up to 3 times.
- Malformed SQL returned a controlled error.
- Unsafe calculator input was rejected by the input guardrail.
- Suspicious output was blocked by the output guardrail.
- Python source files compiled successfully with python -m compileall .\app.
- Langfuse traces were verified for agent and tool execution.
