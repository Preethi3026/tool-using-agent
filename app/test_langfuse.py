from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

langfuse = get_client()

if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

langfuse.flush()