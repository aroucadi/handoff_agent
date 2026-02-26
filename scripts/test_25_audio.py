import asyncio
import os
from google import genai
from google.genai.types import (
    LiveConnectConfig, Modality
)

async def test_live_api():
    api_key = "AIzaSyBKJl-jMO9GA_gp77l9f7DnfwLIdUj3PMo"
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    
    try:
        live_config = LiveConnectConfig(response_modalities=[Modality.AUDIO])
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"Connected to {model_name}")
            print("Sending 10 seconds of raw PCM audio chunks...")
            
            # Simulate 10 seconds of audio data being sent linearly
            for _ in range(20):
                audio_bytes = b'\x00' * 8192
                await session.send_realtime_input(audio={"data": audio_bytes, "mime_type": "audio/pcm"})
                await asyncio.sleep(0.5)

            print("Done sending. Waiting for response...")
            async for response in session.receive():
                print("Got response")
                break

    except Exception as e:
        print(f"Error testing: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test_live_api())

