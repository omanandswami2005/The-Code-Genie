"""
FastAPI server for CodeGenie interactive interface.
Handles WebSocket connections and agent orchestration.
"""

import json
import uuid
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agents.coordinator import create_codegenie_coordinator, default_event_callback

# --- FastAPI App Setup ---
app = FastAPI(title="CodeGenie", description="Automated Software Development System")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- ADK Setup ---
session_service = InMemorySessionService()
active_sessions = {}

def get_agent_for_session():
    """Creates the agent hierarchy for a new session."""
    return create_codegenie_coordinator(after_event_callback=default_event_callback)

# --- Routes ---
@app.get("/")
async def get_index(request: Request):
    """Serves the main application interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles WebSocket connections for real-time agent interaction.
    
    This endpoint manages:
    - Session creation and cleanup
    - Message routing between UI and agents
    - Real-time streaming of agent responses
    - User approval workflow
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())
    print(f"🔗 Client connected. Session ID: {session_id}")
    
    try:
        # Initialize agent hierarchy and session
        root_agent = get_agent_for_session()
        runner = Runner(
            agent=root_agent, 
            app_name="CodeGenieInteractive", 
            session_service=session_service
        )
        
        # Create ADK session
        adk_session = await session_service.create_session(
            user_id=session_id, 
            session_id=session_id, 
            app_name="CodeGenieInteractive"
        )
        adk_session.state["srs_approved"] = False
        
        # Store session
        active_sessions[session_id] = {
            "runner": runner, 
            "session": adk_session
        }
        
        print(f"✅ Session {session_id} initialized successfully")
        
        # Main message handling loop
        while True:
            # Wait for client message
            data = await websocket.receive_text()
            message = json.loads(data)
            print(f"📨 Received from {session_id}: {message}")

            current_session = active_sessions[session_id]["session"]
            
            if message['type'] == 'prompt':
                await handle_prompt_message(websocket, runner, current_session, message, session_id)
            elif message['type'] == 'approve':
                await handle_approval_message(websocket, runner, current_session, session_id)
            else:
                print(f"⚠️ Unknown message type: {message['type']}")

    except WebSocketDisconnect:
        print(f"🔌 Client {session_id} disconnected")
    except Exception as e:
        print(f"❌ Error in session {session_id}: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error", 
                "content": f"An error occurred: {str(e)}"
            }))
        except:
            pass
    finally:
        # Cleanup session
        if session_id in active_sessions:
            del active_sessions[session_id]
            print(f"🧹 Session {session_id} cleaned up")

async def handle_prompt_message(websocket: WebSocket, runner: Runner, session, message: dict, session_id: str):
    """
    Handles user prompt messages and streams agent responses.
    
    Args:
        websocket: WebSocket connection
        runner: ADK runner instance
        session: ADK session object
        message: User message data
        session_id: Session identifier
    """
    # Store user prompt in session state
    session.state['initial_prompt'] = message['content']
    
    print(f"🤖 Starting agent processing for session {session_id}")
    
    # Run agent with streaming
    events = runner.run_async(
        session_id=session.id, 
        user_id=session_id, 
        new_message=Content(parts=[Part(text=message['content'])])
    )

    # Stream agent responses
    async for event in events:
        try:
            # Handle turn completion
            if event.turn_complete or event.interrupted:
                completion_message = {
                    "type": "turn_complete",
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(completion_message))
                continue
            
            # Handle partial text responses
            if event.content and event.content.parts:
                part = event.content.parts[0]
                if part.text and event.partial:
                    text_message = {
                        "type": "partial_text",
                        "data": part.text
                    }
                    await websocket.send_text(json.dumps(text_message))
                    
        except Exception as e:
            print(f"❌ Error processing event: {e}")

    # Send final SRS draft
    srs_draft = session.state.get("srs_draft", "No SRS draft was generated.")
    await websocket.send_text(json.dumps({
        "type": "srs_draft", 
        "content": srs_draft
    }))
    
    print(f"📋 SRS draft sent to client {session_id}")

async def handle_approval_message(websocket: WebSocket, runner: Runner, session, session_id: str):
    """
    Handles user approval and continues the workflow.
    
    Args:
        websocket: WebSocket connection
        runner: ADK runner instance
        session: ADK session object
        session_id: Session identifier
    """
    # Set approval flag
    session.state['srs_approved'] = True
    
    await websocket.send_text(json.dumps({
        "type": "status", 
        "content": "✅ SRS approved! Continuing workflow..."
    }))
    
    print(f"✅ SRS approved for session {session_id}, continuing workflow")
    
    # Continue agent execution
    events = runner.run_async(
        session_id=session.id, 
        user_id=session_id, 
        new_message=Content(parts=[Part(text="Please proceed with the approved SRS.")])
    )
    
    # Process continuation events
    async for event in events:
        if event.content and event.content.parts:
            part = event.content.parts[0]
            if part.text and not event.partial:
                await websocket.send_text(json.dumps({
                    "type": "workflow_update",
                    "content": part.text
                }))

    # Send completion message
    await websocket.send_text(json.dumps({
        "type": "status", 
        "content": "🎉 Workflow phase completed! Ready for next steps."
    }))

if __name__ == '__main__':
    import uvicorn
    print("🚀 Starting CodeGenie Interactive Server...")
    print("🌐 Open http://127.0.0.1:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)