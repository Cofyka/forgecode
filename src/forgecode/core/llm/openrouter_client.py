import openai
from .llm_client import LLMClient, LLMCodeGenerationError
from typing import List, Optional, Dict, Any
import json

class OpenRouterLLMClient(LLMClient):
    """Implementation of LLMClient using OpenAI's SDK with OpenRouter API."""

    def __init__(self, api_key: str):
        """Initializes the OpenRouter LLM client."""
        self.client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    def request_completion(self, model: str, messages: List[Any], schema: Optional[Dict[str, Any]] = None) -> Any:
        """Sends messages to the OpenRouter hosted model and returns the response."""
        
        try:
            if schema:
                response_structured = self.client.beta.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=schema,
                )
                result = json.loads(response_structured.choices[0].message.content)
                return result
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            return response.choices[0].message.content
            
        except openai.APIError as e:
            raise LLMCodeGenerationError(f"OpenRouter API error: {str(e)}")
        except openai.APIConnectionError as e:
            raise LLMCodeGenerationError(f"Failed to connect to OpenRouter API: {str(e)}")
        except openai.RateLimitError as e:
            raise LLMCodeGenerationError(f"OpenRouter rate limit exceeded: {str(e)}")
        except openai.AuthenticationError as e:
            raise LLMCodeGenerationError(f"OpenRouter authentication error: {str(e)}")
        except openai.BadRequestError as e:
            raise LLMCodeGenerationError(f"Bad request to OpenRouter API: {str(e)}")
        except Exception as e:
            raise LLMCodeGenerationError(f"Unexpected error with OpenRouter: {str(e)}")