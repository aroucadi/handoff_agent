import asyncio
import os
from google import genai
from google.genai.types import (
    LiveConnectConfig,
    Content,
    Part,
    FunctionDeclaration,
    Modality,
    Tool,
)

async def send_continuous_audio(session):
    print("Started background audio task")
    try:
        while True:
            audio_bytes = b'\x00' * 3200
            await session.send_realtime_input(audio={"data": audio_bytes, "mime_type": "audio/pcm"})
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        print("Stopped audio task")

async def test_live_api():
    api_key = "AIzaSyBKJl-jMO9GA_gp77l9f7DnfwLIdUj3PMo"
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    
    try:
        declarations = [
            FunctionDeclaration(
                name="read_index",
                description="Read the index node.",
                parameters={"type": "object", "properties": {"client_id": {"type": "string"}}, "required": ["client_id"]},
            )
        ]

        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            system_instruction=Content(parts=[Part.from_text(text="Execute read_index immediately based on system event.")]),
            tools=[Tool(function_declarations=declarations)]
        )
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"Connected to {model_name}")
            
            # Start background mic streaming
            audio_task = asyncio.create_task(send_continuous_audio(session))

            # Send kickoff
            kickoff = ("SYSTEM_EVENT: The user has just connected. Execute the 'read_index' tool immediately. client_id='123'. "
                      "After receiving the tool result, greet the user ALOUD with a summary.")
            print("Sending kickoff...")
            await session.send_realtime_input(text=kickoff)
            
            async for response in session.receive():
                if response.server_content and response.server_content.model_turn:
                    pass # just receive silently
                
                if response.tool_call:
                    print(f"Got tool call: {response.tool_call.function_calls[0].name}")
                
                if response.server_content and response.server_content.turn_complete:
                    print("Turn complete")
                    break

            audio_task.cancel()

    except Exception as e:
        print(f"Error testing: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test_live_api())

