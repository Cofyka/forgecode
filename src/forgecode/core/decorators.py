import functools
import inspect
import sys
from typing import Type, Callable
import typing

from forgecode.core.forgecode import ForgeCode
from forgecode.core.utils.normalize_args import normalize_args

try:
    import pydantic
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = Type  # Just a placeholder for type hints

def type_to_schema(annotation) -> dict:
    """
    Convert a Python type hint into a JSON Schema fragment.

    Supports basic types (int, float, str, bool, None), pydantic BaseModel subclasses,
    types like List[...] and Dict[...]. For dictionaries with str keys, uses
    "additionalProperties" to define the value type.

    :param annotation: A type annotation.
    :return: A dictionary representing the JSON Schema.
    """
    # If pydantic is available and the annotation is a Pydantic model, return its schema.
    if PYDANTIC_AVAILABLE and isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation.model_json_schema()

    basic_types = {
        int: {"type": "integer"},
        float: {"type": "number"},
        str: {"type": "string"},
        bool: {"type": "boolean"},
        list: {"type": "array", "items": {}},
        dict: {"type": "object"},
        type(None): {"type": "null"}
    }
    
    # If the annotation is one of the basic types, return its schema.
    if annotation in basic_types:
        return basic_types[annotation]
    
    # Handle the 'Any' type from typing.
    if annotation is typing.Any:
        return {}  # No restrictions
    
    # Handle generic types like List[...] and Dict[...].
    if hasattr(annotation, "__origin__"):
        origin = annotation.__origin__
        args = annotation.__args__
        if origin is list and args:
            return {"type": "array", "items": type_to_schema(args[0])}
        elif origin is dict and args:
            # Only use additionalProperties if the key is a string.
            if args[0] is str:
                return {"type": "object", "additionalProperties": type_to_schema(args[1])}
            return {"type": "object"}
        
    # Fallback: return an empty schema.
    return {}

def forge(prompt: str = None, modules: list = None, schema: dict = None):
    """
    Decorator to integrate ForgeCode execution with a function.

    This decorator will:
      - Infer a JSON Schema from the function’s return type if no explicit schema is provided.
      - Bind the function’s arguments into a dictionary.
      - Collect modules for additional context.
      - Instantiate and run ForgeCode with the combined settings.

    :param prompt: A string prompt for ForgeCode.
    :param schema: Optional explicit JSON Schema.
    :param modules: Optional modules to include; must be a list.
    :return: A decorator that wraps the function with ForgeCode execution.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract prompt from docstring if not provided explicitly.
            func_prompt = prompt or (func.__doc__.strip() if func.__doc__ else None)
            if not func_prompt:
                raise ValueError(f"No prompt provided for function '{func.__name__}', either in decorator or docstring.")
            
            # Infer the return type's schema if not explicitly provided.
            type_hints = typing.get_type_hints(func)
            return_type = type_hints.get("return")
            inferred_schema = type_to_schema(return_type) if return_type is not None else {}
            schema_dict = schema or inferred_schema

            # Bind the function's arguments to get a dictionary of parameter names to values.
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            args= bound_args.arguments

            # Create a dictionary for modules if provided.
            modules_dict = {}
            if modules:
                if isinstance(modules, list):
                    for idx, module in enumerate(modules):
                        name = getattr(module, '__name__', None)
                        # Use a generated name if the module is a lambda or doesn't have a name.
                        if not name or name == "<lambda>":
                            name = f"lambda{idx}"
                        modules_dict[name] = module
                elif isinstance(modules, dict):
                    modules_dict = modules

            result = ForgeCode(
                prompt=func_prompt,
                schema=schema_dict,
                args=normalize_args(args),
                modules=modules_dict
            ).run()

            # Convert dict result back to a pydantic model if the return type is a pydantic BaseModel.
            if PYDANTIC_AVAILABLE and return_type is not None and isinstance(return_type, type) and issubclass(return_type, BaseModel):
                try:
                    result_model = return_type.model_validate(result)
                except Exception as e:
                    print(f"Error converting result to Pydantic model: {e}")
                    raise
                return result_model

            return result
        return wrapper
    return decorator