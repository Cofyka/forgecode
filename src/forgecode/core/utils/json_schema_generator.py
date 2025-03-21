
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
        # We'll build an 'array' schema.
        if len(obj) > 0:
            # Check if all items are the same type
            first_item_type = type(obj[0])
            same_type = all(isinstance(item, first_item_type) for item in obj)
            
            if same_type and all(item is None for item in obj):
                # All items are None
                return {
                    "type": "array",
                    "items": {"type": "null"}
                }
            elif same_type and None not in obj:
                # All items have the same non-None type
                item_schema = generate_schema(obj[0])
                return {
                    "type": "array",
                    "items": item_schema
                }
            else:
                # Handle mixed types (including None values)
                # Get unique types in the array, excluding None
                non_none_items = [item for item in obj if item is not None]
                
                if not non_none_items:
                    # If after excluding None we have nothing, just return array of nulls
                    return {
                        "type": "array",
                        "items": {"type": "null"}
                    }
                
                # Get schema for a sample of each unique type
                type_samples = {}
                for item in non_none_items:
                    item_type = type(item).__name__
                    if item_type not in type_samples:
                        type_samples[item_type] = item
                
                # Create "anyOf" schema with each type represented
                schemas = [generate_schema(sample) for sample in type_samples.values()]
                
                # Add null type if we have None values
                if None in obj:
                    schemas.append({"type": "null"})
                
                return {
                    "type": "array",
                    "items": {"anyOf": schemas}
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