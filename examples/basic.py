
from forgecode import ForgeCode
from forgecode.core.llm.openai_client import OpenAILLMClient
from config import get_env_var

ForgeCode.set_default_llm(OpenAILLMClient(api_key=get_env_var("OPENAI_API_KEY")))
ForgeCode.set_default_model("gpt-4o")

forge = ForgeCode(
    prompt="sum two numbers",
    schema_from={"sum": 5}
)
res = forge.run(args={"a": 3, "b": 2})

print(res)
# print(forge.get_code())