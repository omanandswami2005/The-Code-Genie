from dotenv import load_dotenv
from google.adk.agents import Agent


load_dotenv()


# Define Agents
root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash-exp",
    description="Orchestrates Agent.",
    instruction="Manage the workflow for SRS creation, structure generation, and voice feedback."
)

srs_creator = Agent(
    name="srs_creator",
    model="gemini-2.0-flash-exp",
    description="Creates the Software Requirements Specification (SRS).",
    instruction="First respond with 'I will update the SRS based on your input' then generate an SRS based on user input describing the podcast requirements."
)

structure_creator = Agent(
    name="structure_creator",
    model="gemini-2.0-flash-exp",
    description="Creates the project structure based on SRS.",
    instruction="First respond with 'I will create the project structure based on the SRS' then design a project structure based on the provided SRS."
)

code_generator = Agent(
    name="code_generator",
    model="gemini-2.0-flash-exp",
    description="Generates code based on the project structure.",
    instruction="Generate Python code files based on the given structure."
)

voice_agent = Agent(
    name="voice_agent",
    model="gemini-2.0-flash-exp",
    description="Generates audio feedback in Hindi and Marathi."
)