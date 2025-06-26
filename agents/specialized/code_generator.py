# codegenie/agents/specialized/code_generator.py

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from utils.config import MODEL_ID

def create_code_generator_agent(
    module_name: str,
    executor_tool: FunctionTool,
    vc_commit_tool: FunctionTool,
    after_event_callback
) -> LlmAgent:
    """
    Factory function to create a specialized Code Generator Agent.

    Each instance of this agent is responsible for generating code for a single,
    specific module. It's designed for parallel execution.

    Args:
        module_name: The name of the module this agent is responsible for (e.g., 'database_setup', 'user_routes').
        executor_tool: The tool needed to save the generated code to a file.
        vc_commit_tool: The tool needed to commit the newly created file.
        after_event_callback: The callback function for voice feedback.

    Returns:
        A configured, specialized instance of the LlmAgent for code generation.
    """
    # We dynamically create the instruction using the module_name to give the agent
    # a highly specific and focused task.
    agent_instruction = f"""
    You are an expert software engineer assigned to develop the '{module_name}' module.
    Your work must be clean, efficient, and well-documented.

    Your workflow is as follows:
    1.  Thoroughly read the project's SRS from the state key 'srs_draft'.
    2.  Write the complete, production-ready Python code for the '{module_name}' module.
        Ensure your code includes necessary imports, comments, and error handling.
    3.  Output the full code as your primary response.
    4.  IMPORTANT: After outputting the code, you must save it to a file. To do this,
        you need a tool that can write content. Let's assume you need to create a file
        and will use a command for that. Use the `_execute_secure_command` tool
        with `command='python'` and `args=['-c', 'with open(\"your_file.py\", \"w\") as f: f.write(\"...\")']`
        to write the code to the appropriate file in the project structure.
        Replace `your_file.py` and the `...` with the actual file name and code.
    5.  After the file is successfully saved, use the `_git_commit` tool to commit
        your work. Provide a clear commit message that starts with 'feat({module_name}):'.

    Execute these steps in precise order. The code must be generated and saved before it is committed.
    """

    code_generator = LlmAgent(
        # The agent's name is also made unique by the module name
        name=f"CodeGeneratorAgent_{module_name.replace(' ', '_')}",
        model=MODEL_ID,
        instruction=agent_instruction,
        # This agent needs both tools to accomplish its task
        tools=[executor_tool, vc_commit_tool],
        after_agent_callback=after_event_callback
    )

    return code_generator