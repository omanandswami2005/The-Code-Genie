# codegenie/agents/specialized/directory_structure.py

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from utils.config import MODEL_ID

def create_directory_structure_agent(
    executor_tool: FunctionTool, 
    after_event_callback
) -> LlmAgent:
    """
    Factory function to create the Directory Structure Agent.

    This agent is responsible for designing and creating the project's
    directory structure based on the SRS. It is equipped with the
    ExecutorTool to securely create files and folders.

    Args:
        executor_tool: The security-hardened tool for executing OS commands.
        after_event_callback: The callback function to post events to the voice queue.

    Returns:
        An configured instance of the LlmAgent for directory creation.
    """
    agent_instruction = """
    You are a senior software architect responsible for designing and implementing
    the project's foundational directory structure.

    Your task has two steps:
    1.  Read the Software Requirements Specification (SRS) provided in the state key 'srs_draft'.
    2.  Based on the SRS, determine a logical and scalable directory structure. This typically
        includes folders for source code, tests, documentation, and configuration.

    To create the structure, you MUST use the '_execute_secure_command' tool.
    - To create a directory, call the tool with: `command='mkdir'`, `args=['path/to/directory_name']`.
    - To create an empty file, call the tool with: `command='touch'`, `args=['path/to/file_name.ext']`.

    Execute these commands sequentially for all required directories and initial empty files
    (like `__init__.py`, `main.py`, `requirements.txt`, etc.).

    Once you have issued all the necessary commands to build the structure, output a final
    confirmation message summarizing the created structure.
    """

    directory_agent = LlmAgent(
        name="DirectoryStructureAgent",
        model=MODEL_ID,
        instruction=agent_instruction,
        tools=[executor_tool], # This agent is only given the executor tool
        after_agent_callback=after_event_callback
    )
    
    return directory_agent