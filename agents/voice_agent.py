# codegenie/agents/voice_agent.py

from google.adk.agents import LlmAgent
from utils.config import MODEL_ID

def create_voice_agent() -> LlmAgent:
    """
    Creates a specialized agent that acts as a text-to-speech engine.

    This agent receives a text prompt and its primary goal is to generate
    an audio representation of that text, which the system can then stream.
    
    Returns:
        An LlmAgent configured for TTS.
    """
    
    # The instruction is simple: don't be a conversationalist, just convert text.
    # The actual audio generation is enabled via the RunConfig when calling the agent.
    agent_instruction = """You are an Voice Agent."""
    
    voice_agent = LlmAgent(
        name="VoiceAgent",
        model=MODEL_ID,
        instruction=agent_instruction,
        description="A specialized voice Agent."
    )
    
    return voice_agent