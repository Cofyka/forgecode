import openai
from .llm_client import LLMClient
from typing import List, Optional, Dict, Any
import json

class OpenAILLMClient(LLMClient):
    """Implementation of LLMClient using OpenAI's SDK."""

    def __init__(self, api_key: str):
        """Initializes the OpenAI LLM client."""
        self.client = openai.OpenAI(api_key=api_key)

    def request_completion(self, model: str, messages: List[Any], schema: Optional[Dict[str, Any]] = None) -> Any:
        """Sends messages to the OpenAI model and returns the response."""
        
        if schema:
            response_structured = self.client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=schema,
            )
            return json.loads(response_structured.choices[0].message.content)
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content