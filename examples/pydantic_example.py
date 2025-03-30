import config

from forgecode import ForgeCode
from forgecode.core.llm.openai_client import OpenAILLMClient

from pydantic import BaseModel

class SumModel(BaseModel):
    sum: int

class Sum2Model(BaseModel):
    sum: int
    a: int
    b: int

class Sum3Model(BaseModel):
    sum: int
    methodology: str
    a: int
    b: int

forge = ForgeCode(
    prompt="sum two numbers",
    schema=SumModel
)

result = forge.run(args={"a": 3, "b": 2})

print(result)
print(forge.run(args={"a": 3, "b": 2}, schema=Sum2Model))
print(forge.run(args={"a": 3, "b": 2}, schema=Sum3Model))

