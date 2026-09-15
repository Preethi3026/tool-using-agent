from dotenv import load_dotenv
import os

load_dotenv()

from agent import agent, validate_user_input, validate_agent_output
from langfuse import get_client
from langfuse.langchain import CallbackHandler


langfuse = get_client()

langfuse_handler = CallbackHandler(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"]
)


question = input("Ask the agent a question: ")

error = validate_user_input(question)

if error:
    print(f"\nInput rejected: {error}")
    raise SystemExit


response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": question,
            }
        ]
    },
    config={
        "callbacks": [langfuse_handler]
    }
)


print("\nFinal answer:")

for message in reversed(response["messages"]):
    if type(message).__name__ == "AIMessage" and message.content:
        final_answer = validate_agent_output(message.content)
        print(final_answer)
        break

langfuse.flush()