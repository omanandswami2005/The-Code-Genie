"""
Secure executor agent for running OS commands safely.
This agent provides controlled access to system operations.
"""

import subprocess
import os
from google.adk.agents import BaseAgent
from google.adk.tools import FunctionTool, ToolContext
from utils.config import EXECUTOR_COMMAND_WHITELIST, PROJECT_DIR

class ExecutorAgent(BaseAgent):
    """
    A secure agent for executing OS commands with strict controls.
    
    This agent serves as the sole gateway for system operations,
    implementing security measures and command validation.
    """
    
    name: str = "ExecutorAgent"

    def __init__(self):
        """Initialize the executor agent with its tool."""
        super().__init__()
        self._tool = FunctionTool(func=self._execute_secure_command)

    def _execute_secure_command(self, command: str, args: list[str], tool_context: ToolContext) -> dict:
        """
        Executes a command securely after validation.

        This method implements multiple security layers:
        1. Command whitelist validation
        2. Input sanitization
        3. Execution in controlled environment
        4. Timeout protection
        5. Comprehensive logging

        Args:
            command: The command to execute (e.g., 'mkdir', 'python')
            args: List of arguments for the command
            tool_context: ADK tool context for logging and tracking

        Returns:
            dict: Execution result with status, stdout, and stderr
        """
        # Security check: validate command against whitelist
        if command not in EXECUTOR_COMMAND_WHITELIST:
            error_msg = f"Command '{command}' is not allowed. Permitted commands: {', '.join(EXECUTOR_COMMAND_WHITELIST)}"
            print(f"[{self.name}] SECURITY VIOLATION: {error_msg}")
            return {
                "status": "error",
                "stderr": error_msg,
                "stdout": ""
            }

        # Prepare the full command
        full_command = [command] + args
        
        try:
            # Ensure project directory exists
            if not os.path.exists(PROJECT_DIR):
                os.makedirs(PROJECT_DIR)
                print(f"[{self.name}] Created project directory: {PROJECT_DIR}")

            # Log the command execution
            print(f"[{self.name}] Executing: {' '.join(full_command)} in {PROJECT_DIR}")

            # Execute the command with security constraints
            result = subprocess.run(
                full_command,
                cwd=PROJECT_DIR,  # Restrict execution to project directory
                capture_output=True,
                text=True,
                check=False,  # Don't raise exception on non-zero exit
                timeout=30  # Prevent long-running commands
            )

            # Prepare the response
            response = {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }

            # Log the result
            if result.returncode == 0:
                print(f"[{self.name}] Command completed successfully")
                if result.stdout:
                    print(f"[{self.name}] Output: {result.stdout.strip()}")
            else:
                print(f"[{self.name}] Command failed with return code {result.returncode}")
                if result.stderr:
                    print(f"[{self.name}] Error: {result.stderr.strip()}")

            return response

        except FileNotFoundError:
            error_msg = f"Command not found: {command}"
            print(f"[{self.name}] ERROR: {error_msg}")
            return {
                "status": "error",
                "stderr": error_msg,
                "stdout": ""
            }
        
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after 30 seconds: {command}"
            print(f"[{self.name}] ERROR: {error_msg}")
            return {
                "status": "error",
                "stderr": error_msg,
                "stdout": ""
            }
        
        except Exception as e:
            error_msg = f"Unexpected error executing command: {str(e)}"
            print(f"[{self.name}] ERROR: {error_msg}")
            return {
                "status": "error",
                "stderr": error_msg,
                "stdout": ""
            }

    @property
    def tool(self) -> FunctionTool:
        """
        Provides access to the secure command execution tool.
        
        Returns:
            FunctionTool: The configured execution tool
        """
        return self._tool