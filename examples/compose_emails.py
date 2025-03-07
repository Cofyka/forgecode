import urllib.request
import json

from forgecode import ForgeCode
from forgecode.core.llm.openai_client import OpenAILLMClient
from config import get_env_var

ForgeCode.set_default_llm(OpenAILLMClient(api_key=get_env_var("OPENAI_API_KEY")))
ForgeCode.set_default_model("gpt-4o")

BASE_URL = "https://jsonplaceholder.typicode.com"

def fetch_users():
    """Fetch 10 users."""
    with urllib.request.urlopen(f"{BASE_URL}/users") as response:
        return json.loads(response.read().decode())

def fetch_posts():
    """Fetch 100 posts."""
    with urllib.request.urlopen(f"{BASE_URL}/posts") as response:
        return json.loads(response.read().decode())

def fetch_comments():
    """Fetch 500 comments."""
    with urllib.request.urlopen(f"{BASE_URL}/comments") as response:
        return json.loads(response.read().decode())

def summarize(posts, comments):
    return ForgeCode._default_llm.request_completion(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize the posts and comments for the user"},
            {"role": "user", "content": f"Posts: {posts}\n\nComments: {comments}"},
        ]
    )

forge = ForgeCode(
    prompt="Create personalized email content for each user. Include a summary of their posts and comments.",
    modules={
        "fetch_users": fetch_users,
        "fetch_posts": fetch_posts,
        "fetch_comments": fetch_comments,
        "summarize_llm": summarize,
    },
    schema_from=[
        {'user_id': 1, 'name': 'John Doe', 'title': 'Title', 'body': 'Body'},
    ],
    max_retries=5
)
emails = forge.run()
print(emails)