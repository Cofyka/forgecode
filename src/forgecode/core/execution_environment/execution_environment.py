from abc import ABC, abstractmethod
from typing import Any, Dict

class ExecutionEnvironment(ABC):
    """Abstract class defining an execution environment for running Python code."""

    @abstractmethod
    def execute_code(self, code: str, context: Dict[str, Any]) -> Any:
        """
        Execute the given code and return the result.

        Raises:
            CodeExecutionError: If an error occurs during code execution.
        """
        pass

class CodeExecutionError(Exception):
    """Custom exception for code execution errors."""
    def __init__(self, message: str, stack_trace: str, variables: Dict[str, Any]):
        super().__init__(message)
        self.stack_trace = stack_trace
        self.variables = variables
