from typing import Any, Dict, List, Union
from dataclasses import dataclass
import json

@dataclass
class LimiterConfig:
    """Configuration for data structure size limits."""
    max_array_length: int = 50
    max_object_members: int = 20
    max_string_length: int = 1000
    max_depth: int = 10
    max_key_length: int = 100
    truncation_indicator: str = "..."

class DataLimiter:
    """Handles size limitation for complex data structures."""

    def __init__(self, config: LimiterConfig = None):
        self.config = config or LimiterConfig()

    def limit(self, data: Any, depth: int = 0) -> Any:
        """Limit the size of a data structure."""
        if depth > self.config.max_depth:
            return self.config.truncation_indicator

        if isinstance(data, (int, float, bool, type(None))):
            return data
        elif isinstance(data, str):
            return self._limit_string(data)
        # elif isinstance(data, pd.DataFrame):
        #     return self.limit(data.to_dict(orient="records"), depth + 1)
        elif isinstance(data, (list, tuple)):
            return self._limit_array(data, depth)
        elif isinstance(data, dict):
            return self._limit_object(data, depth)
        else:
            return self._limit_string(str(data))

    def _limit_string(self, value: str, max_length: int = None) -> str:
        """Limit string length and add truncation indicator if needed."""
        max_length = max_length or self.config.max_string_length
        if len(value) > max_length:
            return value[:max_length] + self.config.truncation_indicator
        return value
    
    def _limit_array(self, arr: Union[list, tuple], depth: int) -> list:
        """Limit array length and add truncation indicator if needed."""
        if len(arr) > self.config.max_array_length:
            limited_arr = [
                self.limit(item, depth + 1) 
                for item in arr[:self.config.max_array_length]
            ]
            limited_arr.append(self.config.truncation_indicator)
            return limited_arr
        return [self.limit(item, depth + 1) for item in arr]

    def _limit_object(self, obj: dict, depth: int) -> dict:
        """Limit the size of a dictionary."""
        limited_obj = {}

        for i, (key, value) in enumerate(obj.items()):
            if i >= self.config.max_object_members:
                limited_obj[self.config.truncation_indicator] = self.config.truncation_indicator
                break

            # Limit key length
            limited_key = self._limit_string(str(key), self.config.max_key_length)

            # Limit value recursively
            limited_obj[limited_key] = self.limit(value, depth + 1)

        return limited_obj

class DataLimiterJson(DataLimiter):

    def calculate_max_config(self, data: Any) -> LimiterConfig:
        """
        Calculate the maximum config values based on the given data structure.
        """
        def _traverse(data, depth=0):
            nonlocal max_depth, max_array_length, max_object_members, max_key_length, max_string_length
            max_depth = max(max_depth, depth)
            
            if isinstance(data, (int, float, bool, type(None))):
                return
            elif isinstance(data, str):
                max_string_length = max(max_string_length, len(data))
            # elif isinstance(data, pd.DataFrame):
            #     _traverse(data.to_dict(orient="records"), depth + 1)
            elif isinstance(data, (list, tuple)):
                max_array_length = max(max_array_length, len(data))
                for item in data:
                    _traverse(item, depth + 1)
            elif isinstance(data, dict):
                max_object_members = max(max_object_members, len(data))
                for key, value in data.items():
                    max_key_length = max(max_key_length, len(str(key)))
                    _traverse(value, depth + 1)
        
        # Initialize max values
        max_depth = 0
        max_array_length = 0
        max_object_members = 0
        max_key_length = 0
        max_string_length = 0
        
        # Traverse the data structure
        _traverse(data)
        
        # Return a LimiterConfig with calculated maximum values
        return LimiterConfig(
            max_array_length=max_array_length,
            max_object_members=max_object_members,
            max_string_length=max_string_length,
            max_depth=max_depth,
            max_key_length=max_key_length,
            truncation_indicator=self.config.truncation_indicator,
        )

    def limit_json(
            self, 
            data: Any, 
            max_json_chars: int,
            strategy: str = "breadth-first"
    ) -> str:
        if strategy == "breadth-first":
            self.config = self.calculate_max_config(data)

        limited_data = self.limit(data)
        json_str = json.dumps(limited_data, ensure_ascii=False)

        if len(json_str) <= max_json_chars:
            return json_str
        
        # Reduce will try 100 times, if no reduce happens after 100 iterations, it will give up.
        # It will restart iterations if a reduction is made.
        max_iterations = 100
        iterations = 0

        while iterations < max_iterations:
            reduced = self._reduce_config(strategy)
            # if reduced, reset iterations
            if reduced:
                iterations = 0
            # if not reduced, increment iterations
            else:
                iterations += 1

            limited_data = self.limit(data)
            json_str = json.dumps(limited_data, ensure_ascii=False)

            # print(json_str)

            if len(json_str) <= max_json_chars:
                break

        return json_str
        
    def _reduce_config(self, strategy: str) -> bool:
        """
        Reduce the config parameters according to the chosen strategy.
        Return True if we actually reduced something, False if we can't.
        """

        # depth-first is in early stages of development
        if strategy == "breadth-first":
            return self._reduce_breadth_first()
        else:
            return False
    
    def _reduce_breadth_first(self) -> bool:
        """
        Strategy #2: 'Breadth-first' - proportionally reduce
        all main config params in small decrements each iteration.
        Return True if a reduction was made, False if not possible.
        """
        did_reduce = False
        
        # We'll define a small factor to reduce each step, e.g., 0.8 (reduce by 20%).
        factor = 0.8

        # if self.config.max_depth > 1:
        #     new_depth = int(self.config.max_depth * factor)
        #     new_depth = max(1, new_depth)
        #     did_reduce = True
        #     self.config.max_depth = new_depth

        if self.config.max_array_length > 1:
            new_array_length = int(self.config.max_array_length * factor)
            new_array_length = max(1, new_array_length)
            did_reduce = True
            self.config.max_array_length = new_array_length

        # if self.config.max_object_members > 1:
        #     new_object_members = int(self.config.max_object_members * factor)
        #     new_object_members = max(1, new_object_members)
        #     did_reduce = True
        #     self.config.max_object_members = new_object_members

        # if self.config.max_key_length > 1:
        #     new_key_length = int(self.config.max_key_length * factor)
        #     new_key_length = max(1, new_key_length)
        #     did_reduce = True
        #     self.config.max_key_length = new_key_length

        if self.config.max_string_length > 1:
            new_string_length = int(self.config.max_string_length * factor)
            new_string_length = max(1, new_string_length)
            did_reduce = True
            self.config.max_string_length = new_string_length

        return did_reduce

def limit_json_data(
    data: Any,
    max_json_chars: int,
    strategy: str = "breadth-first",
    config: LimiterConfig = None
) -> str:
    """
    Convenience function to limit a JSON-compatible data structure.

    Args:
        data (Any): The JSON-compatible data structure to be limited.
        max_json_chars (int): The maximum number of characters allowed in the JSON string.
        strategy (str): The strategy to use for limiting ('breadth-first' or 'depth-first').
        config (LimiterConfig, optional): Custom configuration for the DataLimiter.

    Returns:
        str: The limited JSON string.
    """
    # Initialize DataLimiterJson with the provided or default configuration
    limiter = DataLimiterJson(config=config or LimiterConfig())

    # Perform the JSON limiting
    return limiter.limit_json(data, max_json_chars, strategy=strategy)