# utils/config.py
import os

# --- Model Configuration ---
MODEL_ID = "gemini-2.0-flash"

# --- Project Configuration ---
PROJECT_DIR = os.path.join(os.getcwd(), "generated_project")

# --- Security Configuration ---
# Whitelist of safe commands for the ExecutorAgent
EXECUTOR_COMMAND_WHITELIST = [
    "mkdir",
    "touch",
    "ls",
    "python",
    "pip",
    "git",
    "curl",
    "wget",
    "cp",
    "mv",
    "rm",
    "cd",
    "cat",
    "find",
    "grep",
]

# --- Voice Service Configuration ---
VOICE_VERBOSITY_LEVEL = "detailed" # Can be 'silent', 'summary', 'detailed'
VOICE_PRIORITY = {
    "CRITICAL": 1, # Errors
    "HIGH": 2,     # Major state changes (e.g., SRS approved)
    "MEDIUM": 3,   # Task completion (e.g., module generated)
    "LOW": 4       # Detailed explanations
}