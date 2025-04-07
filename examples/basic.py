import config

from forgecode import ForgeCode, OpenAILLMClient

forge = ForgeCode(
    prompt="sum two numbers",
    schema_from={"sum": 5}
)
res = forge.run(args={"a": 3, "b": 2})

print(res)
# print(forge.get_code())