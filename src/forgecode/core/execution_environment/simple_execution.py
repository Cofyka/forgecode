import io
import traceback
import contextlib
from typing import Any, Dict
from .execution_environment import ExecutionEnvironment, CodeExecutionError

class SimpleExecutionEnvironment(ExecutionEnvironment):
    """Concrete execution environment using Python's exec() with output capture."""
    
    def execute_code(self, code: str, context: Dict[str, Any]) -> Any:
        """
        Executes the given code, capturing stdout/stderr and ensuring the code sets a 'result' variable.
        The 'result' is then returned.

        Parameters:
            code (str): The code to execute.
            context (Dict[str, Any]): The execution context containing the initial variables.

        Returns:
            Any: The 'result' from the executed code.

        Raises:
            CodeExecutionError: If execution fails or 'result' is not set.
        """
        stdout = io.StringIO()
        stderr = io.StringIO()
        local_vars = {}

        try:
            # Use the provided context as execution globals
            execution_context = {**(context or {})}

            # Execute code while capturing stdout and stderr.
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                # Compile first to ensure the syntax is valid.
                compiled_code = compile(code, '<string>', 'exec')
                exec(compiled_code, execution_context, local_vars)
            
            # Ensure the executed code has set a 'result' variable.
            if "result" not in local_vars:
                raise CodeExecutionError(
                    message="Code did not set the 'result' variable.",
                    stack_trace=None,
                    variables=local_vars
                )
            
            return local_vars["result"]
        
        except Exception as e:
            raise CodeExecutionError(
                message=str(e),
                stack_trace=traceback.format_exc(),
                variables=local_vars
            ) from e
        
        finally:
            # Clean up resources.
            stdout.close()
            stderr.close()