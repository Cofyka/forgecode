from .llm.llm_client import LLMClient, LLMCodeGenerationError
from .llm.openai_client import OpenAILLMClient
from .llm.openrouter_client import OpenRouterLLMClient

from .execution_environment.execution_environment import ExecutionEnvironment, CodeExecutionError
from .execution_environment.simple_execution import SimpleExecutionEnvironment

from .persistence.code_persistence import CodePersistence
from .persistence.forgecache import ForgeCache

from .utils.json_schema_generator import generate_schema
from .utils.dict_formatter import format_dict
from .utils.data_limiter import limit_json_data, LimiterConfig
from .utils.imports import PYDANTIC_AVAILABLE, BaseModel

from typing import Any, Dict
from jsonschema import Draft7Validator, SchemaError, validate, ValidationError
import json
import hashlib

from .prompts import CODE_GENERATION_SYSTEM_PROMPT, ADVANCED_CAPABILITIES_PROMPT

class ForgeCode:
    _default_llm = None
    _default_model = None
    _default_exec_env = SimpleExecutionEnvironment()
    _default_code_persistence = ForgeCache()
    _default_max_retries = 3
    _default_enable_self_reference = False
    _default_use_cache = True

    def __init__(
            self, 
            prompt: str = None, 
            args = None, 
            modules = None, 
            schema = None, 
            schema_from = None, 
            llm: LLMClient = None, 
            model: str = None,
            exec_env: ExecutionEnvironment = None,
            code_persistence: CodePersistence = None,
            max_retries: int = None,
            enable_self_reference: bool = None,
            use_cache: bool = None):
        
        """Initializes ForgeCode with an LLM client or falls back to the default client."""
        if llm is None:
            if ForgeCode._default_llm is None:
                raise ValueError(
                    "No LLM client provided, and no default client set. "
                    "Use `ForgeCode.set_default_llm()` or pass an LLM instance explicitly."
                )
            llm = ForgeCode._default_llm

        if not isinstance(llm, LLMClient):
            raise TypeError("llm must be an instance of LLMClient")
        
        if model is None:
            if ForgeCode._default_model is None:
                raise ValueError(
                    "No model provided, and no default model set. "
                    "Use `ForgeCode.set_default_model()` or pass a model explicitly."
                )
            
            model = ForgeCode._default_model

        if exec_env is None:
            exec_env = ForgeCode._default_exec_env

        if code_persistence is None:
            code_persistence = ForgeCode._default_code_persistence

        if max_retries is None:
            max_retries = ForgeCode._default_max_retries
            
        if enable_self_reference is None:
            enable_self_reference = ForgeCode._default_enable_self_reference
            
        if use_cache is None:
            use_cache = ForgeCode._default_use_cache

        # Inputs
        self.prompt = prompt
        self.args = args
        self.modules = modules
        self.schema = schema
        self.schema_from = schema_from
        # Generate schema from provided object
        if schema_from:
            self.schema = generate_schema(schema_from)
        # If pydantic is available
        if PYDANTIC_AVAILABLE:
            # Initialize pydantic_model variable used to store the model
            self.pydantic_model = None

            # If schema is pydantic model
            if isinstance(schema, type) and issubclass(schema, BaseModel):
                # save the model for later instantiation of the result
                self.pydantic_model = schema
                # convert model to json schema
                self.schema = schema.model_json_schema()

        if self.schema is not None:
            self._validate_json_schema(self.schema)

        # LLM
        self.llm = llm
        self.model = model

        self.exec_env = exec_env
        self.code_persistence = code_persistence

        self.max_retries = max_retries
        
        # Enable self-reference to allow nested ForgeCode capabilities
        if enable_self_reference:
            from forgecode.core.decorators import forge
            if isinstance(self.modules, dict):
                self.modules.update({"forge": forge})
            else:
                self.modules = {"forge": forge}
        self.enable_self_reference = enable_self_reference
        
        self.use_cache = use_cache

    @classmethod
    def set_default_llm(cls, llm: LLMClient):
        """Sets the default LLM client for ForgeCode."""
        if not isinstance(llm, LLMClient):
            raise TypeError("llm must be an instance of LLMClient")
        cls._default_llm = llm

    @classmethod
    def set_default_model(cls, model: str):
        """Sets the default model for ForgeCode."""
        cls._default_model = model

    @classmethod
    def set_default_exec_env(cls, exec_env: ExecutionEnvironment):
        """Sets the default execution environment for ForgeCode."""
        cls._default_exec_env = exec_env

    @classmethod
    def set_default_code_persistence(cls, code_persistence: CodePersistence):
        """Sets the default code persistence for ForgeCode."""
        cls._default_code_persistence = code_persistence

    @classmethod
    def set_default_code_persistence(cls, code_persistence: CodePersistence):
        """Sets the default code persistence for ForgeCode."""
        cls._default_code_persistence = code_persistence

    @classmethod
    def set_default_max_retries(cls, max_retries: int):
        """Sets the default maximum number of retries for ForgeCode."""
        cls._default_max_retries = max_retries
        
    @classmethod
    def set_default_enable_self_reference(cls, enable: bool):
        """Sets whether ForgeCode instances should enable self-reference by default."""
        cls._default_enable_self_reference = enable
        
    @classmethod
    def set_default_use_cache(cls, use_cache: bool):
        """Sets whether ForgeCode instances should use code caching by default."""
        cls._default_use_cache = use_cache
        
    @classmethod
    def setup_openai(cls, api_key: str, model: str = "gpt-4o"):
        """
        Convenience method to quickly set up OpenAI as the default LLM provider.
        
        This method configures both the default LLM client and default model in one call.
        
        Args:
            api_key: OpenAI API key for authentication
            model: OpenAI model to use (default: "gpt-4o")
            
        Example:
            ```python
            # Setup OpenAI as the default provider
            ForgeCode.setup_openai(api_key="your-api-key")
            
            # Now you can create ForgeCode instances without specifying the LLM
            forge = ForgeCode(prompt="sum two numbers", args={"a": 3, "b": 2}, schema_from={"sum": 5})
            ```
        """
        openai_client = OpenAILLMClient(api_key=api_key)
        cls.set_default_llm(openai_client)
        cls.set_default_model(model)
        
    @classmethod
    def setup_openrouter(cls, api_key: str, model: str = "openai/gpt-4o-2024-08-06"):
        """
        Convenience method to quickly set up OpenRouter as the default LLM provider.
        
        This method configures both the default LLM client and default model in one call.
        Model must support structured output.
        
        Args:
            api_key: OpenRouter API key for authentication
            model: OpenRouter model to use (default: "openai/gpt-4o-2024-08-06")
            
        Example:
            ```python
            # Setup OpenRouter as the default provider
            ForgeCode.setup_openrouter(api_key="your-api-key")
            
            # Now you can create ForgeCode instances without specifying the LLM
            forge = ForgeCode(prompt="sum two numbers", args={"a": 3, "b": 2}, schema_from={"sum": 5})
            ```
        """
        openrouter_client = OpenRouterLLMClient(api_key=api_key)
        cls.set_default_llm(openrouter_client)
        cls.set_default_model(model)

    @classmethod
    def from_openai(cls, api_key: str, model: str = "gpt-4", **kwargs):
        """
        Alternative constructor: Initializes ForgeCode with OpenAI as the LLM.
        
        Args:
            api_key: OpenAI API key for authentication
            model: OpenAI model to use (default: "gpt-4")
            **kwargs: Additional parameters to pass to ForgeCode constructor
            
        Returns:
            ForgeCode instance configured with OpenAI
            
        Examples:
            ```python
            # Basic usage
            forge = ForgeCode.from_openai(api_key="your-api-key")
            
            # With model specification
            forge = ForgeCode.from_openai(
                api_key="your-api-key", 
                model="gpt-4o",
                prompt="sum two numbers",
                schema_from={"sum": 5}
            )
            ```
        """
        try:
            openai_client = OpenAILLMClient(api_key=api_key)
            
            kwargs_with_defaults = {
                'llm': openai_client,
                'model': model,
                **kwargs
            }
            
            return cls(**kwargs_with_defaults)
            
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")

    def run(
        self, 
        prompt: str = None, 
        args = None, 
        modules = None, 
        schema = None, 
        schema_from = None):
        """Accomplishes the task by generating code based on the provided prompt."""

        if prompt is None:
            if self.prompt is None:
                raise ValueError("No prompt provided")
            prompt = self.prompt

        args_schema = None
        if args is None:
            if self.args is not None:
                args = self.args
        if args is not None:
            args_schema = generate_schema(args)

        modules_str = None
        if modules is None:
            if self.modules is not None:
                modules = self.modules
        if modules is not None:
            modules_str = format_dict(modules)

        if PYDANTIC_AVAILABLE:
            pydantic_model = None

        if schema is None:
            if self.schema is not None:
                schema = self.schema
                if PYDANTIC_AVAILABLE:
                    pydantic_model = self.pydantic_model
        else:
            if PYDANTIC_AVAILABLE:
                if isinstance(schema, type) and issubclass(schema, BaseModel):
                    # save the model for later instantiation of the result
                    pydantic_model = schema
                    # convert model to json schema
                    schema = schema.model_json_schema()
        if schema_from is not None:
            schema = generate_schema(schema_from)

        if schema is not None:
            self._validate_json_schema(schema)

        # Iterative variables
        attempt = 0

        previous_code = None
        error = None
        stack_trace = None
        local_vars = None

        result = None
        #

        while attempt < self.max_retries:
            attempt += 1
            try:
                system_prompt = CODE_GENERATION_SYSTEM_PROMPT.format(
                    prompt=prompt,
                    modules=modules_str,
                    args=args_schema,
                    result_schema=schema if schema else "No schema provided",
                    advanced_capabilities=ADVANCED_CAPABILITIES_PROMPT if self.enable_self_reference else "",
                    previous_code=f"## Previous code:\n{previous_code}" if previous_code else "",
                    error=f"## Error:\n{error}" if error else "",
                    code_traceback=f"## Code Traceback:\n{stack_trace}" if stack_trace else "",
                    local_vars=f"## Local Variables:\n{limit_json_data(local_vars, 10000, config=LimiterConfig(truncation_indicator = "..."))}" if local_vars else ""
                )

                fgce_hash = self._compute_hash(prompt, args, modules, schema)
                code = None

                # Try to load the code only on the first iteration if caching is enabled,
                # because all subsequent iterations mean that the code was invalid
                if attempt == 1 and self.use_cache:
                    code = self.code_persistence.load(fgce_hash)

                if code is None:
                    code = self.generate_code(system_prompt)

                # Save the code for the next iteration
                previous_code = code

                # Execute the code (it may raise error)
                result = self.exec_env.execute_code(previous_code, {**(modules or {}), 'args': args})

                # Validate the result against the schema. It raises ValidationError if the result is invalid
                if schema is not None:
                    self._validate_result(result, schema)

                # If the result is valid and caching is enabled, save the code to the cache
                if self.use_cache:
                    self.code_persistence.save(fgce_hash, code)

                break
            except CodeExecutionError as e:
                error = str(e)
                stack_trace = e.stack_trace
                local_vars = e.variables
                continue
            except ValidationError as e:
                error = f"Result did not match the expected schema: {e.message}"
                stack_trace = None
                local_vars = None
                continue
            except LLMCodeGenerationError as e:
                raise ForgeCodeError(f"LLM code generation error: {str(e)}")
            except Exception as e:
                error = str(e)
                stack_trace = None
                local_vars = None
                continue

        if attempt == self.max_retries:
            raise ForgeCodeError(
                f"""Failed to generate valid code after {self.max_retries} attempts
                \nPrompt: {prompt}
                \nArgs schema: {args_schema}
                \nModules string: {modules_str}
                \nSchema: {schema}
                \nPrevious code:\n{previous_code}
                \nError:\n{error if error else "No error"}
                \nCode Traceback:\n{stack_trace if stack_trace else "No traceback"}"""
            )

        # If the result should be a Pydantic model, return the result as a model instance
        if PYDANTIC_AVAILABLE and pydantic_model is not None:
            return pydantic_model.model_validate(result)

        return result

    def _validate_json_schema(self, schema: Dict[str, Any]):
        """Validates that the JSON schema itself is well-formed."""
        try:
            Draft7Validator.check_schema(schema)
        except SchemaError as e:
            raise ValueError(f"Invalid JSON schema provided: {e.message}")


    def _validate_result(self, result: Any, schema: Dict[str, Any]):
        """Validate the structure of the result using a schema."""
        validate(instance=result, schema=schema)

    def generate_code(self, prompt: str) -> str:
        """Generates code based on a given prompt using the LLM."""
        
        completion = self.llm.request_completion(
            self.model, 
            messages=[
                {"role": "system", "content": "You are a code generator. Don't include python markdown like ```python or ```"},
                {"role": "user", "content": prompt}
            ], 
            schema={
                "type": "json_schema",
                "json_schema": {
                    "name": "CodeGeneration",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"}
                        },
                        "required": ["code"]
                    }
                }
            }
        )

        if 'code' not in completion:
            raise LLMCodeGenerationError("LLM failed to generate code in the required format")

        return completion['code']
    
    def get_code(self) -> str:
        """Returns the cached code if available and caching is enabled."""
        if not self.use_cache:
            return None
        return self.code_persistence.load(self._compute_hash(prompt=self.prompt, args=self.args, modules=self.modules, schema=self.schema))
    
    def _compute_hash(self, prompt, args, modules, schema) -> str:
        """
        Computes a unique hash based on the input arguments that define the ForgeCode entity.
        Parameters not provided are taken from the instance attributes.
        This hash can be used to cache or log generated code for a given configuration.
        """

        args_schema = generate_schema(args) if args is not None else None
        modules_str = format_dict(modules) if modules is not None else None

        data = {
            "prompt": prompt if prompt is not None else None,
            "args_schema": args_schema if args_schema is not None else None,
            "modules_str": modules_str if modules_str is not None else None,
            "schema": schema if schema is not None else None
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    
class ForgeCodeError(Exception):
    """Custom forgecode exception for execution errors."""
    def __init__(self, message: str):
        super().__init__(message)