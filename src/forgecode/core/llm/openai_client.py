import openai
from .llm_client import LLMClient, LLMCodeGenerationError
from typing import List, Optional, Dict, Any
import json

class OpenAILLMClient(LLMClient):
    """Implementation of LLMClient using OpenAI's SDK."""

    def __init__(self, api_key: str):
        """Initializes the OpenAI LLM client."""
        self.client = openai.OpenAI(api_key=api_key)

    def request_completion(self, model: str, messages: List[Any], schema: Optional[Dict[str, Any]] = None) -> Any:
        """Sends messages to the OpenAI model and returns the response."""
        
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
            raise LLMCodeGenerationError(f"OpenAI API error: {str(e)}")
        except openai.APIConnectionError as e:
            raise LLMCodeGenerationError(f"Failed to connect to OpenAI API: {str(e)}")
        except openai.RateLimitError as e:
            raise LLMCodeGenerationError(f"OpenAI rate limit exceeded: {str(e)}")
        except openai.AuthenticationError as e:
            raise LLMCodeGenerationError(f"OpenAI authentication error: {str(e)}")
        except openai.BadRequestError as e:
            raise LLMCodeGenerationError(f"Bad request to OpenAI API: {str(e)}")
        except Exception as e:
            raise LLMCodeGenerationError(f"Unexpected error with OpenAI: {str(e)}")