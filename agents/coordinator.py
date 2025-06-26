"""
Main coordinator agent that orchestrates the entire CodeGenie workflow.
This is the top-level agent that manages all other agents and workflows.
"""

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.events import Event
from utils.config import MODEL_ID
from agents.specialized.srs_creation_interactive import create_srs_creation_agent_interactive
from agents.specialized.directory_structure import create_directory_structure_agent
from agents.specialized.code_generator import create_code_generator_agent
from agents.tools.executor import ExecutorAgent
from agents.tools.version_control import VersionControlAgent

def create_codegenie_coordinator(after_event_callback=None) -> LlmAgent:
    """
    Creates the main CodeGenie Coordinator agent.
    
    This agent serves as the entry point and orchestrates the entire workflow:
    1. SRS Creation (interactive loop)
    2. Directory Structure Design
    3. Code Generation (parallel)
    4. Testing and Documentation
    
    Returns:
        LlmAgent: The configured coordinator agent
    """
    
    # Create tool agents
    executor_agent = ExecutorAgent()
    version_control_agent = VersionControlAgent()
    
    # Create the SRS creation agent (interactive loop)
    srs_creation_agent = create_srs_creation_agent_interactive()
    
    # Create directory structure agent
    directory_structure_agent = create_directory_structure_agent(
        executor_tool=executor_agent.tool,
        after_event_callback=after_event_callback
    )
    
    # Create the project lifecycle sequential agent
    project_lifecycle = SequentialAgent(
        name="ProjectLifecycle",
        sub_agents=[
            srs_creation_agent,
            directory_structure_agent,
            # Additional agents will be added here as we expand
        ]
    )
    
    # Create the main coordinator
    coordinator = LlmAgent(
        name="CodeGenieCoordinator",
        model=MODEL_ID,
        instruction="""You are the master coordinator for CodeGenie, an automated software development system.

Your primary responsibilities:
1. Understand user intent and project requirements
2. Delegate tasks to appropriate specialized agents
3. Manage the overall project workflow
4. Provide clear communication to users

When a user wants to start a new project:
- Transfer to the 'ProjectLifecycle' agent to begin the structured workflow
- The workflow includes: SRS creation → Directory structure → Code generation

When a user wants to update an existing project:
- Analyze what needs to be updated
- Delegate to appropriate specialized agents

Always provide clear, helpful responses and keep the user informed of progress.""",
        sub_agents=[project_lifecycle],
        after_agent_callback=after_event_callback
    )
    
    return coordinator

def default_event_callback(context: CallbackContext, event: Event) -> None:
    """
    Default callback for handling agent events.
    This can be used for logging, voice feedback, or other cross-cutting concerns.
    """
    if event.is_final_response():
        print(f"[{context.agent_name}] Completed task")
        if event.content and event.content.parts:
            content_preview = event.content.parts[0].text[:100] if event.content.parts[0].text else "No content"
            print(f"[{context.agent_name}] Output preview: {content_preview}...")