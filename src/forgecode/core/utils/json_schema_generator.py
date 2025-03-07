
def generate_schema(obj):
    """
    Recursively generate a JSON Schema from a Python object.
    """

    # Identify the Python type and map it to JSON Schema
    if isinstance(obj, dict):
        # We'll build an 'object' schema with properties
        properties = {}
        required = []
        for key, value in obj.items():
            properties[key] = generate_schema(value)
            required.append(key)
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    elif isinstance(obj, list):
        # We'll build an 'array' schema. We take a naive approach and assume
        # all items have the same type. If the array is empty, we just say "any items".
        if len(obj) > 0:
            # generate schema from the first item to represent 'items'
            item_schema = generate_schema(obj[0])
            return {
                "type": "array",
                "items": item_schema
            }
        else:
            return {
                "type": "array"
                # No 'items' key because it's empty
            }

    elif isinstance(obj, str):
        return {"type": "string"}

    elif isinstance(obj, bool):
        return {"type": "boolean"}

    elif isinstance(obj, int):
        # If you want to differentiate int vs float more precisely, you can
        # check for float separately. By JSON Schema definitions, "integer"
        # is also a "number", but let's be specific if we know it's int.
        return {"type": "integer"}

    elif isinstance(obj, float):
        return {"type": "number"}

    elif obj is None:
        # The JSON Schema spec 2020-12 supports "null" type
        return {"type": "null"}

    else:
        # Fallback for any type not handled explicitly above
        return {}