import json
import uuid
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agents.specialized.srs_creation_interactive import create_srs_creation_agent_interactive

# --- FastAPI App Setup ---
app = FastAPI()

# Mounts the 'static' directory under the '/static' URL path
app.mount("/static", StaticFiles(directory="static"), name="static")

# Locates the 'templates' directory for rendering HTML
templates = Jinja2Templates(directory="templates")


# --- ADK Setup ---
# A global session service can be shared among runners
session_service = InMemorySessionService()

# In-memory storage for active sessions. In production, this could be Redis.
active_sessions = {}

def get_agent_for_session():
    """Builds the agent hierarchy for a new session."""
    return create_srs_creation_agent_interactive()


# --- Main HTML Route ---
@app.get("/")
async def get_index(request: Request):
    """Serves the main index.html file."""
    return templates.TemplateResponse("index.html", {"request": request})

# --- WebSocket Route ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handles a single client's WebSocket connection and agent interaction."""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    print(f"Client connected. Creating session_id: {session_id}")
    
    # Each connection gets its own runner and agent instance
    root_agent = get_agent_for_session()
    runner = Runner(agent=root_agent, app_name="CodeGenieInteractive", session_service=session_service)
    
    # Create and store the ADK session object
    adk_session = await session_service.create_session(user_id=session_id, session_id=session_id, app_name="CodeGenieInteractive")
    adk_session.state["srs_approved"] = False
    
    active_sessions[session_id] = {"runner": runner, "session": adk_session}

    try:
        # Loop indefinitely to handle multiple messages from the same client
        while True:
            # Wait for a message from the client (e.g., prompt or approval)
            data = await websocket.receive_text()
            message = json.loads(data)
            print(f"Received from client {session_id}: {message}")

            current_session = active_sessions[session_id]["session"]
            
            if message['type'] == 'prompt':
                # Update state with the initial prompt from the user
                current_session.state['initial_prompt'] = message['content']
                
                # Use the asynchronous runner.run_async() method
                # This returns an async generator that we can loop over.
                events = runner.run_async(session_id=current_session.id, user_id=session_id, new_message=Content(parts=[Part(text=message['content'])]))

                async for event in events:
                    print(f"[AGENT TO CLIENT]: {event}")
                    if event.turn_complete or event.interrupted:
                        message = {
                            "turn_complete": event.turn_complete,
                            "interrupted": event.interrupted,
                        }
                        print(message)
                        await websocket.send_text(json.dumps(message))
                        print(f"[AGENT TO CLIENT]: {message}")
                        continue
                    # Read the Content and its first Part
                    part: Part = (
                        event.content and event.content.parts and event.content.parts[0]
                    )
                    if not part:
                        continue
                    
                    # If it's text and a parial text, send it
                    if part.text and event.partial:
                        message = {
                            "mime_type": "text/plain",
                            "data": part.text
                        }
                        print(message)
                        await websocket.send_text(json.dumps(message))
                        print(f"[AGENT TO CLIENT]: text/plain: {message}")

                # After the agent's turn is complete, the state will be updated.
                srs_draft = current_session.state.get("srs_draft", "Agent did not produce a draft.")
                
                # Send the final generated SRS back to the UI
                await websocket.send_text(json.dumps({"type": "srs_draft", "content": srs_draft}))

            elif message['type'] == 'approve':
                # User clicked approve
                current_session.state['srs_approved'] = True
                await websocket.send_text(json.dumps({"type": "status", "content": "Approval received! Resuming agent workflow..."}))
                
                # Run the agent AGAIN with run_async. This time it will see the approval and complete.
                events = runner.run_async(session_id=current_session.id, user_id=session_id, new_message=Content(parts=[Part(text="Please proceed.")]))
                async for event in events:
                    pass # We just need the loop to complete

                final_response = "Workflow complete! The loop agent has finished."
                
                await websocket.send_text(json.dumps({"type": "status", "content": final_response}))

    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected.")
    except Exception as e:
        print(f"An unexpected error occurred in session {session_id}: {e}")
    finally:
        # Clean up the session from memory when the connection closes
        if session_id in active_sessions:
            del active_sessions[session_id]
            print(f"Session {session_id} cleaned up.")


if __name__ == '__main__':
    import uvicorn
    print("Starting CodeGenie Interactive Server with FastAPI and Uvicorn...")
    print("Open http://127.0.0.1:8000 in your browser.")
    uvicorn.run(app, host="0.0.0.0", port=8000)