# ForgeCode

ForgeCode is a Python library that enables dynamic code generation using LLMs. It allows developers to write high-level code by specifying a goal, schema, arguments, and modules, and then iteratively generates executable code that satisfies the given constraints. On subsequent calls, it remembers and reuses the last successful execution.

## Installation

```bash
pip install forgecode
```

Or with Poetry:

```bash
poetry add forgecode
```

## Quick Start

```python
from forgecode import ForgeCode

# Simple example - summing two numbers
forge = ForgeCode.from_openai(api_key="your-api-key", model="gpt-4o") # Initialize with OpenAI
result = forge.run(
    prompt="sum two numbers",   # Goal
    args={"a": 3, "b": 2},      # Arguments
    schema_from={"sum": 5}      # Schema for output
)

print(result)                   # {"sum": 5}
print(forge.get_code())         # View the generated code
```

## Key Features

- **Goal-oriented code generation**: Specify what you want, not how to do it
- **Schema validation**: Ensure generated code produces output matching your specifications
- **Execution environment**: Safely execute generated code
- **Caching**: Remember successful solutions for faster repeated executions
- **Iterative refinement**: Automatically fix errors through multiple generation attempts
- **Module passing**: Provide access to specific modules or functions to the generated code

## Real-World Use Cases

### API Data Transformation

Fetch and transform data from external APIs with minimal code:

```python
import urllib.request
import json

# API endpoint functions
def fetch_users():
    with urllib.request.urlopen("https://jsonplaceholder.typicode.com/users") as response:
        return json.loads(response.read().decode())

def fetch_posts():
    with urllib.request.urlopen("https://jsonplaceholder.typicode.com/posts") as response:
        return json.loads(response.read().decode())

def fetch_comments():
    with urllib.request.urlopen("https://jsonplaceholder.typicode.com/comments") as response:
        return json.loads(response.read().decode())

# Create a forge with access to these API functions
forge = ForgeCode(
    prompt="Get all users along with their posts and each post's comments.",
    modules={
        "users": fetch_users,
        "posts": fetch_posts,
        "comments": fetch_comments
    },
    schema_from=[
        {
            "id": 1,
            "name": "John Doe",
            "posts": [
                {
                    "id": 101,
                    "title": "Post Title",
                    "body": "Post content",
                    "comments": [
                        {
                            "id": 1001,
                            "name": "Commenter",
                            "email": "commenter@example.com",
                            "body": "Comment content"
                        }
                    ]
                }
            ]
        }
    ]
)

enriched_data = forge.run()
```

### Natural Language Data Query Interface

Create a dynamic query interface for your APIs:

```python
def query_api(prompt):
    """Convert natural language into API calls"""
    forge = ForgeCode(
        prompt=prompt,
        modules=api_modules,  # Dictionary of API functions
        schema={},  # Flexible schema
        max_retries=5
    )
    return forge.run()

# Use natural language to query your API
print(query_api("Get all the comments for the first post"))
print(query_api("Get all incomplete todos for user with ID 3"))
```

### Schema Transformation

Easily transform data structures with the builtin schema transformer:

```python
from forgecode.builtins.schema_transform import schema

input_data = [
    {"first_name": "Alice", "last_name": "Johnson", "year_of_birth": 1993, "location": "New York"},
    {"first_name": "Bob", "last_name": "Smith", "year_of_birth": 1998, "location": "San Francisco"},
]

desired_output_example = [
    {'fullname': 'John Doe', 'age': 30, 'location': 'Chicago'},
]

# Transform input data to match the desired output format
transformed_data = schema(input_data).to(desired_output_example)
```

### Content Generation

Create personalized content by combining data sources:

```python
forge = ForgeCode(
    prompt="Create personalized email content for each user. Include a summary of their posts and comments.",
    modules={
        "fetch_users": fetch_users,
        "fetch_posts": fetch_posts,
        "fetch_comments": fetch_comments,
        "summarize_llm": summarize,  # Function using LLM to summarize content
    },
    schema_from=[
        {'user_id': 1, 'name': 'John Doe', 'title': 'Email Subject', 'body': 'Email Body'},
    ],
)

personalized_emails = forge.run()
```

## How It Works

1. **Define your goal**: Provide a clear prompt describing what you want to achieve
2. **Specify constraints**: Add schemas, arguments, or module access as needed
3. **Execute**: ForgeCode generates code, executes it, and validates the output
4. **Iterative refinement**: If execution fails, ForgeCode automatically retries with error context
5. **Caching**: Successful code is stored for reuse in subsequent calls with the same inputs

### Important Details

- **Code regeneration**: ForgeCode uses a hash-based caching mechanism and regenerates code whenever any of these inputs change:
  - Prompt text
  - Arguments structure/schema
  - Provided modules
  - Output schema

- **Module idempotency**: Modules provided to ForgeCode must be idempotent (produce the same output when called multiple times with the same input). This is critical because ForgeCode may run these modules multiple times during the iterative code refinement process.

## Advanced Configuration

```python
# Set global defaults
ForgeCode.set_default_llm(OpenAILLMClient(api_key="your-api-key"))
ForgeCode.set_default_model("gpt-4o")
ForgeCode.set_default_max_retries(5)

# Custom execution environment
from forgecode.core.execution_environment.execution_environment import ExecutionEnvironment
ForgeCode.set_default_exec_env(my_custom_environment)

# Custom persistence
from forgecode.core.persistence.code_persistence import CodePersistence
ForgeCode.set_default_code_persistence(my_custom_storage)
```

## License

MIT