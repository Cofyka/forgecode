"""
Shared imports and flags for the forgecode package.
"""
from typing import Type

# Check for pydantic availability
try:
    import pydantic
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = Type  # Just a placeholder for type hints