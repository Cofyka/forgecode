import urllib.request
import json
from forgecode import ForgeCode
from forgecode.core.llm.openai_client import OpenAILLMClient
from config import get_env_var

ForgeCode.set_default_llm(OpenAILLMClient(api_key=get_env_var("OPENAI_API_KEY")))
ForgeCode.set_default_model("gpt-4o")

BASE_URL = "https://jsonplaceholder.typicode.com"

# Functions for fetching data from each endpoint
def fetch_posts():
    """Fetch 100 posts."""
    with urllib.request.urlopen(f"{BASE_URL}/posts") as response:
        return json.loads(response.read().decode())

def fetch_comments():
    """Fetch 500 comments."""
    with urllib.request.urlopen(f"{BASE_URL}/comments") as response:
        return json.loads(response.read().decode())

def fetch_albums():
    """Fetch 100 albums."""
    with urllib.request.urlopen(f"{BASE_URL}/albums") as response:
        return json.loads(response.read().decode())

def fetch_photos():
    """Fetch 5000 photos."""
    with urllib.request.urlopen(f"{BASE_URL}/photos") as response:
        return json.loads(response.read().decode())

def fetch_todos():
    """Fetch 200 todos."""
    with urllib.request.urlopen(f"{BASE_URL}/todos") as response:
        return json.loads(response.read().decode())

def fetch_users():
    """Fetch 10 users."""
    with urllib.request.urlopen(f"{BASE_URL}/users") as response:
        return json.loads(response.read().decode())

api_modules = {
    "posts": fetch_posts,
    "comments": fetch_comments,
    "albums": fetch_albums,
    "photos": fetch_photos,
    "todos": fetch_todos,
    "users": fetch_users,
}

def query_api(prompt):
    forge = ForgeCode(
        prompt=prompt,
        modules=api_modules,
        schema={},
        max_retries=5
    )
    return forge.run()

print(query_api("Get two random users names"))
print(query_api("Get all the comments for the first post"))
print(query_api("Get all the todos for the first user"))