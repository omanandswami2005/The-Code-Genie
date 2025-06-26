"""
Agent responsible for designing and creating project directory structures.
This agent analyzes the SRS and creates appropriate folder hierarchies.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from utils.config import MODEL_ID

def create_directory_structure_agent(
    executor_tool: FunctionTool, 
    after_event_callback=None
) -> LlmAgent:
    """
    Creates a directory structure agent for project organization.
    
    This agent:
    1. Analyzes the SRS to understand project requirements
    2. Designs an appropriate directory structure
    3. Uses the executor tool to create the structure
    
    Args:
        executor_tool: Tool for executing OS commands securely
        after_event_callback: Optional callback for event handling
        
    Returns:
        LlmAgent: Configured directory structure agent
    """
    
    agent_instruction = """You are a senior software architect specializing in project organization and directory structure design.

Your responsibilities:
1. Read the Software Requirements Specification (SRS) from the state key 'srs_draft'
2. Analyze the project requirements to determine the optimal directory structure
3. Design a logical, scalable directory hierarchy
4. Create the directory structure using the available tools

DIRECTORY DESIGN PRINCIPLES:
- Follow industry best practices for the target technology stack
- Separate concerns (source code, tests, documentation, configuration)
- Plan for scalability and maintainability
- Include standard files (README, requirements, configuration files)

IMPLEMENTATION PROCESS:
1. Analyze the SRS to understand:
   - Project type and technology stack
   - Expected modules and components
   - Testing requirements
   - Documentation needs

2. Design the structure including:
   - Source code directories
   - Test directories
   - Documentation folders
   - Configuration files
   - Build and deployment folders

3. Use the '_execute_secure_command' tool to create:
   - Directories: command='mkdir', args=['path/to/directory']
   - Empty files: command='touch', args=['path/to/file.ext']

4. Create essential files like:
   - __init__.py files for Python packages
   - README.md for documentation
   - requirements.txt for dependencies
   - Configuration files as needed

EXECUTION GUIDELINES:
- Create directories before files
- Use relative paths from the project root
- Follow naming conventions for the target language
- Include placeholder files to establish structure

After creating the structure, provide a summary of what was created and why."""

    return LlmAgent(
        name="DirectoryStructureAgent",
        model=MODEL_ID,
        instruction=agent_instruction,
        tools=[executor_tool],
        after_agent_callback=after_event_callback
    )