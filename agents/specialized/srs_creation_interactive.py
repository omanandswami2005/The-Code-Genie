"""
Interactive SRS creation agent using a loop for iterative refinement.
This agent manages the complete SRS creation workflow with user feedback.
"""

from google.adk.agents import LoopAgent
from agents.specialized.srs_writer import create_srs_writer_agent
from agents.specialized.approval_checker import create_approval_checker

def create_srs_creation_agent_interactive(after_event_callback=None) -> LoopAgent:
    """
    Creates an interactive SRS creation agent that loops until user approval.
    
    This agent implements the iterative SRS refinement process:
    1. SRS Writer creates/refines the specification
    2. Approval Checker determines if user has approved
    3. Loop continues until approval is received
    
    Args:
        after_event_callback: Optional callback for event handling
        
    Returns:
        LoopAgent: Configured interactive SRS creation agent
    """
    
    # Create the SRS writer agent
    srs_writer = create_srs_writer_agent(after_event_callback=after_event_callback)
    
    # Create the approval checker
    approval_checker = create_approval_checker()
    
    # Create the loop agent that coordinates the iterative process
    srs_loop = LoopAgent(
        name="SRSCreationLoop",
        sub_agents=[srs_writer, approval_checker],
        max_iterations=10  # Prevent infinite loops
    )
    
    return srs_loop