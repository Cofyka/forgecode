
from forgecode import ForgeCode
from forgecode.builtins.schema_transform import schema
from forgecode.core.llm.openai_client import OpenAILLMClient
from config import get_env_var

ForgeCode.set_default_llm(OpenAILLMClient(api_key=get_env_var("OPENAI_API_KEY")))
ForgeCode.set_default_model("gpt-4o")

input_data = [
    {"first_name": "Alice", "last_name": "Johnson", "year_of_birth": 1993, "location": "New York"},
    {"first_name": "Bob", "last_name": "Smith", "year_of_birth": 1998, "location": "San Francisco"},
    {"first_name": "Charlie", "last_name": "Brown", "year_of_birth": 1988, "location": "Chicago"},
]

desired_output_example = [
    {'fullname': 'John Doe', 'age': 30, 'location': 'Chicago'},
]

res = schema(input_data).to(desired_output_example)
print(res)