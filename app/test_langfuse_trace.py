from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

langfuse = get_client()

print("Creating test trace...")

with langfuse.start_as_current_observation(
    as_type="span",
    name="project2-test-trace",
    input={"test": "hello"},
) as span:
    span.update(output={"status": "success"})

langfuse.flush()

print("Test trace sent.")