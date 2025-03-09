def normalize_args(args):
    """
    Recursively converts Pydantic models to dictionaries while keeping other data unchanged.

    :param args: Dictionary of function arguments.
    :return: A dictionary where Pydantic models are converted to plain Python objects.
    """
    try:
        from pydantic import BaseModel
        def convert(obj):
            if isinstance(obj, BaseModel):
                return obj.model_dump()
            elif isinstance(obj, list):
                return [convert(item) for item in obj]  # Normalize lists
            elif isinstance(obj, dict):
                return {key: convert(value) for key, value in obj.items()}  # Normalize dict values
            return obj  # Keep other types unchanged

        return convert(args)

    except ImportError:
        return args  # If Pydantic is not available, return args as is