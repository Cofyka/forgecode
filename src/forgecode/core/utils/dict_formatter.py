
import inspect

def format_dict(d) -> str:
    formatted = []
    for key, value in d.items():
        if callable(value):  # Check if the value is a callable (function/method)
            try:
                signature = inspect.signature(value)  # Get the function's signature
                formatted.append(f"{key}{signature} (type: function)")
            except ValueError:
                # Handle cases where the signature cannot be determined
                formatted.append(f"{key} (type: function)")
        elif isinstance(value, type(__import__('sys'))):  # Check if the value is a module
            formatted.append(f"{key} (type: module, name: {value.__name__})")
        else:
            formatted.append(f"{key} (type: {type(value).__name__})")
    return "\n".join(formatted)