import config
from config import get_env_var

from forgecode import ForgeCode, forge, OpenRouterLLMClient

ForgeCode.set_default_llm(OpenRouterLLMClient(api_key=get_env_var("OPENROUTER_API_KEY")))
ForgeCode.set_default_model("mistralai/mistral-small-24b-instruct-2501") # Model must support structured output (https://openrouter.ai/models?order=newest&supported_parameters=structured_outputs)

@forge()
def geo_distance(p1_lat: float, p1_lng: float, p2_lat: float, p2_lng: float) -> float:
    """Calculates straight-line distance (km) between two geographical points."""
    pass

belgrade_coords = (44.7866, 20.4489)
paris_coords = (48.8566, 2.3522)
res = geo_distance(*belgrade_coords, *paris_coords)
print(res)