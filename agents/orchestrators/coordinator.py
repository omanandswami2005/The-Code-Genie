# agents/orchestrators/coordinator.py
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from utils.config import MODEL_ID

def create_codegenie_coordinator(
    srs_creation_agent: LlmAgent,
    directory_structure_agent: LlmAgent,
    code_generator_agents: list[LlmAgent],
    after_event_callback
) -> LlmAgent:
    """Assembles and returns the master CodeGenie Coordinator agent."""

    # 4. Parallel agent for concurrent code generation
    parallel_code_gen = ParallelAgent(
        name="ParallelCodeGeneration",
        sub_agents=code_generator_agents
    )

    # 3. Sequential agent for the main project lifecycle
    project_lifecycle = SequentialAgent(
        name="ProjectLifecycle",
        sub_agents=[
            srs_creation_agent,
            directory_structure_agent,
            parallel_code_gen,
            # testing_agent,
            # documentation_agent
        ]
    )

    # 2. Top-level Coordinator Agent
    # This agent decides which major workflow to start.
    coordinator = LlmAgent(
        name="CodeGenieCoordinator",
        model=MODEL_ID,
        instruction="""You are the master coordinator for CodeGenie. Your job is to understand the user's intent.
- If the user wants to start a new project, delegate the task by calling 'transfer_to_agent' with agent_name 'ProjectLifecycle'.
- If the user wants to update an existing project, delegate to 'UpdaterAgent'.
- Handle all other general queries yourself.""",
        after_agent_callback=after_event_callback,
        sub_agents=[project_lifecycle] # Makes ProjectLifecycle available for transfer
    )
    return coordinator