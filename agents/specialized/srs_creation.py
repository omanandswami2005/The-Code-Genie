# agents/specialized/srs_creation.py
from typing import AsyncGenerator
from google.adk.agents import LlmAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from utils.config import MODEL_ID

# A custom agent to check for the loop termination condition
class UserApprovalChecker(BaseAgent):
    """Checks if the user has approved the SRS to terminate the loop."""
    name: str = "UserApprovalChecker"

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # In a real system, this would check a database or a user input signal.
        # Here, we simulate it by checking a state variable.
        is_approved = ctx.session.state.get("srs_approved", False)
        if is_approved:
            print("[UserApprovalChecker] SRS has been approved. Escalating to exit loop.")
        # escalate=True signals the parent LoopAgent to stop iterating.
        yield Event(author=self.name, actions=EventActions(escalate=is_approved))

def create_srs_creation_agent(after_event_callback) -> LoopAgent:
    """Factory to create the SRS Creation loop agent."""
    srs_writer = LlmAgent(
        name="SRSWriter",
        model=MODEL_ID,
        instruction="""You are an expert technical writer. Based on the user's request in the state 'initial_prompt' and any previous 'srs_draft', refine and generate a Software Requirements Specification (SRS) in Markdown. Store the output in the state key 'srs_draft'.""",
        output_key="srs_draft",
        after_agent_callback=after_event_callback
    )

    approval_checker = UserApprovalChecker()

    srs_loop = LoopAgent(
        name="SRSCreationLoop",
        sub_agents=[srs_writer, approval_checker],
        max_iterations=5
    )
    return srs_loop