from forgecode.core.forgecode import ForgeCode
from typing import Any

class SchemaTransformer:
    def __init__(self, input_obj: Any):
        self.input_obj = input_obj

    def to(self, target: Any) -> Any:
        """
        Transforms the stored input object to match the given schema or example object.

        Args:
            target (dict or Any): The desired output schema or example object.

        Returns:
            dict: The transformed object.
        """
        forge = ForgeCode(
            prompt="Transform input data to match the given schema.",
            args={"input": self.input_obj},
            **({"schema": target} if ("type" in target and "properties" in target) else {"schema_from": target})
        )
        return forge.run()

# Factory function for creating SchemaTransformer instances
def schema(input_obj: Any) -> SchemaTransformer:
    return SchemaTransformer(input_obj)