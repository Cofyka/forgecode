import config

from forgecode import forge

# Example: Generate a Fibonacci function

@forge(prompt="Generate a Fibonacci function")
def fibonacci(n: int) -> list[int]:
    pass  # The decorator will generate the function dynamically

print(fibonacci(10))

# Example: Generate a function that calculates a number using a formula

def formula(a, b):
    return a + b * 2

@forge(prompt="Calculate the number using formula", modules=[formula])
def calculate_num(a: int, b: int) -> int:
    pass

print(calculate_num(5, 10))

# Example: ...

object_example = {
    "name": "John",
    "lastname": "Doe",
    "year_of_birth": 1990,
    "city": "New York"
}

@forge(prompt="Transform the object into a format that has full_name and age fields.")
def transform_object(obj: dict) -> dict:
    pass

print(transform_object(object_example))