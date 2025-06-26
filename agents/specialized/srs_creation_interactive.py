from typing import AsyncGenerator
from google.adk.agents import LlmAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from utils.config import MODEL_ID

class UserApprovalChecker(BaseAgent):
    """Checks if the user has approved the SRS to terminate the loop."""
    name: str = "UserApprovalChecker"

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Checks the session state for the 'srs_approved' flag."""
        is_approved = ctx.session.state.get("srs_approved", False)
        
        status_msg = f"Checking for approval... Current state: {is_approved}"
        print(f"[{self.name}] {status_msg}")

        if is_approved:
            print(f"[{self.name}] Approval found! Escalating to exit loop.")
            yield Event(author=self.name, content=f"Approval received. Continuing workflow.")
        
        yield Event(author=self.name, actions=EventActions(escalate=is_approved))

def create_srs_creation_agent_interactive() -> LoopAgent:
    """Factory to create the interactive SRS Creation loop agent."""
    srs_writer = LlmAgent(
        name="SRSWriter",
        model=MODEL_ID,
        instruction="""You are an expert technical writer. Based on the user's request in the state 'initial_prompt' and any previous 'srs_draft', refine and generate a Software Requirements Specification (SRS) in Markdown. Store the output in the state key 'srs_draft'.""",
        output_key="srs_draft",
    )

    approval_checker = UserApprovalChecker()

    srs_loop = LoopAgent(
        name="SRSCreationLoop",
        sub_agents=[srs_writer, approval_checker],
        max_iterations=5 
    )
    return srs_loop