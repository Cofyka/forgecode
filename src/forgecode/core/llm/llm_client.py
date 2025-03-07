from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def request_completion(self, model: str, messages: List[Any], schema: Optional[Dict[str, Any]] = None) -> Any:
        """Sends a list of messages to the specified LLM model and returns the response."""
        pass