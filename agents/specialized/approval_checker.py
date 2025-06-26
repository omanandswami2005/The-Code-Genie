"""
Custom agent for checking user approval status in interactive workflows.
This agent determines when to continue or terminate iterative processes.
"""

from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

class UserApprovalChecker(BaseAgent):
    """
    Custom agent that checks for user approval to control loop termination.
    
    This agent monitors the session state for approval signals and
    escalates when the user has approved the current iteration.
    """
    
    name: str = "UserApprovalChecker"
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Checks the session state for user approval.
        
        Args:
            ctx: The invocation context containing session state
            
        Yields:
            Event: Status events and escalation signals
        """
        # Check if the user has approved the current SRS
        is_approved = ctx.session.state.get("srs_approved", False)
        
        # Log the current approval status
        status_message = f"Checking approval status: {'APPROVED' if is_approved else 'PENDING'}"
        print(f"[{self.name}] {status_message}")
        
        # Yield a status event
        yield Event(
            author=self.name,
            content=f"Approval status: {'Approved - proceeding with workflow' if is_approved else 'Waiting for user approval'}"
        )
        
        # If approved, escalate to exit the loop
        if is_approved:
            print(f"[{self.name}] User approval detected. Escalating to continue workflow.")
            yield Event(
                author=self.name,
                content="SRS approved by user. Continuing to next phase.",
                actions=EventActions(escalate=True)
            )
        else:
            # Not approved yet, continue the loop
            yield Event(
                author=self.name,
                actions=EventActions(escalate=False)
            )

def create_approval_checker() -> UserApprovalChecker:
    """
    Factory function to create a UserApprovalChecker instance.
    
    Returns:
        UserApprovalChecker: Configured approval checker agent
    """
    return UserApprovalChecker()