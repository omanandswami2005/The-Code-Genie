"""
Version control agent for managing code changes and commits.
This agent provides Git operations and change tracking capabilities.
"""

import subprocess
import os
from google.adk.agents import BaseAgent
from google.adk.tools import FunctionTool, ToolContext
from utils.config import PROJECT_DIR

class VersionControlAgent(BaseAgent):
    """
    Manages version control operations for the generated project.
    
    This agent provides Git functionality including:
    - Repository initialization
    - File staging and commits
    - Diff generation
    - Branch management
    """
    
    name: str = "VersionControlAgent"

    def __init__(self):
        """Initialize the version control agent with its tools."""
        super().__init__()
        self._commit_tool = FunctionTool(func=self._git_commit)
        self._diff_tool = FunctionTool(func=self._git_diff)
        self._init_tool = FunctionTool(func=self._git_init)

    def _git_init(self, tool_context: ToolContext) -> dict:
        """
        Initialize a Git repository in the project directory.
        
        Args:
            tool_context: ADK tool context
            
        Returns:
            dict: Operation result
        """
        try:
            if not os.path.exists(PROJECT_DIR):
                os.makedirs(PROJECT_DIR)
            
            # Check if already a git repository
            if os.path.exists(os.path.join(PROJECT_DIR, '.git')):
                return {
                    "status": "success",
                    "message": "Git repository already exists"
                }
            
            # Initialize git repository
            result = subprocess.run(
                ["git", "init"],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"[{self.name}] Initialized Git repository in {PROJECT_DIR}")
                return {
                    "status": "success",
                    "message": "Git repository initialized successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to initialize Git repository: {result.stderr}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error initializing Git repository: {str(e)}"
            }

    def _git_commit(self, message: str, tool_context: ToolContext) -> dict:
        """
        Commit changes to the Git repository.
        
        Args:
            message: Commit message
            tool_context: ADK tool context
            
        Returns:
            dict: Commit result with hash if successful
        """
        try:
            # Ensure git repository exists
            if not os.path.exists(os.path.join(PROJECT_DIR, '.git')):
                init_result = self._git_init(tool_context)
                if init_result["status"] != "success":
                    return init_result
            
            # Add all files
            add_result = subprocess.run(
                ["git", "add", "."],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if add_result.returncode != 0:
                return {
                    "status": "error",
                    "message": f"Failed to stage files: {add_result.stderr}"
                }
            
            # Commit changes
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if commit_result.returncode == 0:
                # Get the commit hash
                hash_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=PROJECT_DIR,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                commit_hash = hash_result.stdout.strip()[:8] if hash_result.returncode == 0 else "unknown"
                
                print(f"[{self.name}] Committed changes: {message} ({commit_hash})")
                return {
                    "status": "success",
                    "commit_hash": commit_hash,
                    "message": f"Successfully committed: {message}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to commit: {commit_result.stderr}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error during commit: {str(e)}"
            }

    def _git_diff(self, file_path: str = "", tool_context: ToolContext = None) -> dict:
        """
        Generate a diff of changes.
        
        Args:
            file_path: Specific file to diff (empty for all files)
            tool_context: ADK tool context
            
        Returns:
            dict: Diff result
        """
        try:
            # Build the diff command
            cmd = ["git", "diff"]
            if file_path:
                cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "status": "success",
                "diff": result.stdout,
                "message": "Diff generated successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating diff: {str(e)}"
            }

    @property
    def commit_tool(self) -> FunctionTool:
        """Get the commit tool."""
        return self._commit_tool
    
    @property
    def diff_tool(self) -> FunctionTool:
        """Get the diff tool."""
        return self._diff_tool
    
    @property
    def init_tool(self) -> FunctionTool:
        """Get the init tool."""
        return self._init_tool