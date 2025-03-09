import config

from forgecode import forge

# Example: Generate a Fibonacci function

@forge(prompt="Generate a Fibonacci function")
def fibonacci(n: int) -> list[int]:
    pass  # The decorator will generate the function dynamically

print(fibonacci(10))

# # Example: Generate a function that calculates a number using a formula

def formula(a, b):
    return a + b * 2

@forge(prompt="Calculate the number using formula", modules=[formula])
def calculate_num(a: int, b: int) -> int:
    pass

print(calculate_num(5, 10))

# # Example: Transform an object into a different format

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

# Example: Type inference from pydantic models (if available)

try:
    from pydantic import BaseModel
    
    class Person(BaseModel):
        name: str
        age: int
    
    class Greeting(BaseModel):
        message: str
    
    @forge()
    def greet_person(person: Person) -> Greeting:
        """Generate a personalized greeting for a person."""
        pass
    
    greeting = greet_person(Person(name="Alice", age=30))

    print(greeting.message)
    
except ImportError:
    print("Pydantic not installed, skipping Pydantic example")