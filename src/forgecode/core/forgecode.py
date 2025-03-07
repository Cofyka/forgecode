from .llm.llm_client import LLMClient
from .llm.openai_client import OpenAILLMClient

from .execution_environment.execution_environment import ExecutionEnvironment, CodeExecutionError
from .execution_environment.simple_execution import SimpleExecutionEnvironment

from .persistence.code_persistence import CodePersistence
from .persistence.forgecache import ForgeCache

from .utils.json_schema_generator import generate_schema
from .utils.dict_formatter import format_dict
from .utils.data_limiter import limit_json_data, LimiterConfig

from typing import Any, Dict
from jsonschema import Draft7Validator, SchemaError, validate, ValidationError
import json
import hashlib

from .prompts import CODE_GENERATION_SYSTEM_PROMPT

class ForgeCode:
    _default_llm = None
    _default_model = None
    _default_exec_env = SimpleExecutionEnvironment()
    _default_code_persistence = ForgeCache()
    _default_max_retries = 3

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
            max_retries: int = None):
        
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

        # Inputs
        self.prompt = prompt
        self.args = args
        self.modules = modules
        self.schema = schema
        self.schema_from = schema_from
        # Generate schema from provided object
        if schema_from:
            self.schema = generate_schema(schema_from)

        if self.schema is not None:
            self._validate_json_schema(self.schema)

        # LLM
        self.llm = llm
        self.model = model

        self.exec_env = exec_env
        self.code_persistence = code_persistence

        self.max_retries = max_retries

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

        if schema is None:
            if self.schema is not None:
                schema = self.schema
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
                    previous_code=f"## Previous code:\n{previous_code}" if previous_code else "",
                    error=f"## Error:\n{error}" if error else "",
                    code_traceback=f"## Code Traceback:\n{stack_trace}" if stack_trace else "",
                    local_vars=f"## Local Variables:\n{limit_json_data(local_vars, 10000, config=LimiterConfig(truncation_indicator = "..."))}" if local_vars else ""
                )

                code = None

                # Try to load the code only on the first iteration,
                # because all subsequent iterations mean that the code was invalid
                if attempt == 1:
                    code = self.code_persistence.load(self._compute_hash())

                if code is None:
                    code = self.generate_code(system_prompt)

                # Save the code for the next iteration
                previous_code = code

                # Execute the code (it may raise error)
                result = self.exec_env.execute_code(previous_code, {**(modules or {}), 'args': args})

                # Validate the result against the schema. It raises ValidationError if the result is invalid
                if schema is not None:
                    self._validate_result(result, schema)

                # If the result is valid, save the code to the cache and break the loop
                self.code_persistence.save(self._compute_hash(), code)

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

        return completion['code']
    
    def get_code(self) -> str:
        return self.code_persistence.load(self._compute_hash())
    
    def _compute_hash(self) -> str:
        """
        Computes a unique hash based on the input arguments that define the ForgeCode entity.
        Parameters not provided are taken from the instance attributes.
        This hash can be used to cache or log generated code for a given configuration.
        """

        prompt = self.prompt
        args_schema = generate_schema(self.args) if self.args is not None else None
        modules_str = format_dict(self.modules) if self.modules is not None else None
        schema = self.schema

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