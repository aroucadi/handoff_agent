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

async def test_live_api():
    api_key = "AIzaSyBKJl-jMO9GA_gp77l9f7DnfwLIdUj3PMo"
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    
    try:
        live_config = LiveConnectConfig(response_modalities=[Modality.AUDIO])
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"Connected to {model_name}")
            
            # Send text kickoff
            kickoff = "SYSTEM_EVENT: Tell me a huge story about a dragon. Keep talking for 30 seconds."
            await session.send_realtime_input(text=kickoff)
            
            # IMMEDIATELY Send audio chunks endlessly while it's generating the story
            # To simulate the frontend mic being active and sending base64 payloads to the backend
            print("Sending raw audio chunks rapidly...")
            audio_bytes = b'\x00' * 3200
            for _ in range(30):
                await session.send_realtime_input(audio={"data": audio_bytes, "mime_type": "audio/pcm"})
                await asyncio.sleep(0.1)

            print("Done sending audio. Waiting for model response...")
            async for response in session.receive():
                if response.server_content and response.server_content.model_turn:
                    for part in response.server_content.model_turn.parts:
                        if part.text:
                            print(f"[TEXT] {part.text}")
                
                if response.server_content and response.server_content.turn_complete:
                    print("Turn complete")
                    break

    except Exception as e:
        print(f"Error testing: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test_live_api())

