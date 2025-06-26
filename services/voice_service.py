# codegenie/services/voice_service.py

import queue
import threading
import time
from dataclasses import dataclass, field
import pyaudio

from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig
from google.genai.types import Content, Part

from utils.config import VOICE_PRIORITY

# --- Constants for Audio Stream ---
# Gemini models typically generate audio at 24000 Hz sample rate
AUDIO_SAMPLE_RATE = 24000
AUDIO_CHANNELS = 1
# 16-bit audio format
AUDIO_FORMAT = pyaudio.paInt16 

@dataclass(order=True)
class VoiceMessage:
    """A message to be spoken by the voice agent."""
    priority: int
    message: str=field(compare=False)
    source_agent: str=field(compare=False)

# Singleton instance of a thread-safe priority queue
voice_event_queue = queue.PriorityQueue()

class AdkVoiceSynthesizer(threading.Thread):
    """
    A threaded worker that consumes text messages from a queue, sends them to
    a dedicated ADK Voice Agent for TTS conversion, and plays the resulting
    audio bytes using PyAudio.
    """
    def __init__(self, name: str, event_queue: queue.PriorityQueue, runner: Runner):
        super().__init__()
        self.name = name
        self.event_queue = event_queue
        self.runner = runner  # This runner is specifically for the VoiceAgent
        self.daemon = True # Ensure thread exits when main program does
        self.pyaudio_instance = pyaudio.PyAudio()

    def run(self):
        """The main loop for the voice synthesizer thread."""
        print(f"AdkVoiceSynthesizer '{self.name}' started and waiting for messages.")
        while True:
            try:
                # 1. Block until a text message is available from any agent
                message_item = self.event_queue.get()
                print(f"[{self.name} processing]: '{message_item.message}' (From: {message_item.source_agent})")

                # 2. Use the ADK runner to ask the VoiceAgent for speech
                # We need to configure the run to request AUDIO as the output modality
                audio_run_config = RunConfig(response_modalities=["AUDIO"])
                text_content = Content(parts=[Part.from_text(message_item.message)])
                
                # run() is simpler here since we don't need async context
                live_events = self.runner.run(
                    # We don't need persistent sessions for a stateless TTS engine
                    session_id=None, 
                    new_message=text_content,
                    run_config=audio_run_config
                )

                # 3. Process the events to find and stream the audio data
                audio_data_chunks = []
                for event in live_events:
                    part = event.content and event.content.parts and event.content.parts[0]
                    if not part:
                        continue
                    
                    # Check if the part contains audio data
                    is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/")
                    if is_audio and part.inline_data.data:
                        audio_data_chunks.append(part.inline_data.data)

                if audio_data_chunks:
                    self._play_audio_bytes(b"".join(audio_data_chunks))

                self.event_queue.task_done()

            except Exception as e:
                print(f"Error in AdkVoiceSynthesizer '{self.name}': {e}")
                time.sleep(1)

    def _play_audio_bytes(self, audio_data: bytes):
        """Plays raw audio bytes using PyAudio."""
        stream = self.pyaudio_instance.open(
            format=AUDIO_FORMAT,
            channels=AUDIO_CHANNELS,
            rate=AUDIO_SAMPLE_RATE,
            output=True
        )
        print(f"[{self.name} speaking]: Playing {len(audio_data)} bytes of audio.")
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()

# --- Callback function to be used by all agents (Unchanged) ---
from google.adk.agents.callback_context import CallbackContext
from google.adk.events import Event

def post_event_to_voice_queue(
    context: CallbackContext, event: Event
) -> None:
    """ADK callback to post messages to the voice queue."""
    if event.is_final_response():
        message = f"Agent {context.agent_name} has completed its task."
        priority = VOICE_PRIORITY["HIGH"]
        if event.content and event.content.parts and event.content.parts[0].text:
            message += f" The final output is: {event.content.parts[0].text[:100]}..."
            
        vm = VoiceMessage(priority=priority, message=message, source_agent=context.agent_name)
        voice_event_queue.put(vm)