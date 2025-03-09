import config

import urllib.request
import json

from forgecode import ForgeCode

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

forge = ForgeCode(
    prompt="Get all users along with their posts and each post's comments.",
    modules=api_modules,
    schema_from=[
        {
            "id": 1,
            "name": "John Doe",
            "username": "johndoe",
            "email": "johndoe@example.com",
            "address": {
                "street": "123 Main St",
                "suite": "Apt 1",
                "city": "New York",
                "zipcode": "10001"
            },
            "phone": "123-456-7890",
            "website": "johndoe.com",
            "company": {
                "name": "Doe Enterprises",
                "catchPhrase": "Innovate and Elevate",
                "bs": "business solutions"
            },
            "posts": [
                {
                    "id": 101,
                    "title": "Post Title Here",
                    "body": "This is the content of the post.",
                    "comments": [
                        {
                            "id": 1001,
                            "name": "Commenter Name",
                            "email": "commenter@example.com",
                            "body": "This is a comment on the post."
                        }
                    ]
                }
            ]
        }
    ]
)

res = forge.run()

print(res)