import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_env_var(name: str) -> str:
    """Retrieve an environment variable or raise an error if missing."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing {name}. Set it in a .env file or as an environment variable.")
    return value

from forgecode import ForgeCode, OpenAILLMClient

ForgeCode.set_default_llm(OpenAILLMClient(api_key=get_env_var("OPENAI_API_KEY")))
ForgeCode.set_default_model("gpt-4o")