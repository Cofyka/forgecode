"""OpenAI LLM Client implementation for ForgeCode."""

import json
import openai
from typing import List, Optional, Dict, Any

from .llm_client import LLMClient, LLMCodeGenerationError


class OpenAILLMClient(LLMClient):
    """Implementation of LLMClient using OpenAI's SDK."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Initializes the OpenAI LLM client.
        Args:
            api_key: OpenAI API key
            base_url: Optional custom base URL for OpenAI-compatible APIs
            organization: Optional OpenAI organization ID
            timeout: Optional request timeout in seconds
        """
        client_kwargs = {"api_key": api_key}

        if base_url:
            client_kwargs["base_url"] = base_url
        if organization:
            client_kwargs["organization"] = organization
        if timeout:
            client_kwargs["timeout"] = timeout

        self.client = openai.OpenAI(**client_kwargs)

    def request_completion(
        self, model: str, messages: List[Any], schema: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Sends messages to the OpenAI model and returns the response.

        Args:
            model: Model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
            messages: List of message dictionaries with 'role' and 'content'
            schema: Optional JSON schema for structured output

        Returns:
            Parsed response content or structured output

        Raises:
            LLMCodeGenerationError: If API call fails
        """

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
