
import config

from forgecode.builtins.schema_transform import schema

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