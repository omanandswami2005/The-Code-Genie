# agents/tools/executor.py
import subprocess
from google.adk.agents import BaseAgent
from google.adk.tools import FunctionTool, ToolContext
from utils.config import EXECUTOR_COMMAND_WHITELIST, PROJECT_DIR
import os

class ExecutorAgent(BaseAgent):
    """A secure agent for executing OS commands."""
    name: str = "ExecutorAgent"

    def __init__(self):
        super().__init__()
        self._tool = FunctionTool(func=self._execute_secure_command)

    def _execute_secure_command(self, command: str, args: list[str], tool_context: ToolContext) -> dict:
        """
        Executes a command securely after validating it against a whitelist.

        Args:
            command: The command to execute (e.g., 'mkdir').
            args: A list of arguments for the command.

        Returns:
            A dictionary with the execution status, stdout, and stderr.
        """
        if command not in EXECUTOR_COMMAND_WHITELIST:
            return {"status": "error", "stderr": f"Command '{command}' is not allowed."}

        full_command = [command] + args
        try:
            # Ensure the project directory exists
            if not os.path.exists(PROJECT_DIR):
                os.makedirs(PROJECT_DIR)

            result = subprocess.run(
                full_command,
                cwd=PROJECT_DIR, # Run all commands within the project directory
                capture_output=True,
                text=True,
                check=True, # Raise an exception for non-zero exit codes
                timeout=30 # Prevent long-running commands
            )
            return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}
        except FileNotFoundError:
            return {"status": "error", "stderr": f"Command not found: {command}"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "stdout": e.stdout, "stderr": e.stderr}
        except Exception as e:
            return {"status": "error", "stderr": f"An unexpected error occurred: {e}"}

    @property
    def tool(self) -> FunctionTool:
        return self._tool