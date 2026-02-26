import asyncio
import os
import subprocess
from google import genai
from google.genai.types import (
    LiveConnectConfig,
    Content,
    Part,
    Modality,
)

async def test_live_api():
    api_key = "AIzaSyBKJl-jMO9GA_gp77l9f7DnfwLIdUj3PMo"
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    
    try:
        live_config = LiveConnectConfig(response_modalities=[Modality.AUDIO])
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"Connected to {model_name}")
            print("Sending mock webm data...")
            # We send junk data as audio/webm to see if it says 1008 or if it accepts the mime_type 
            await session.send_realtime_input(audio={"data": b"mock_webm_data"*100, "mime_type": "audio/webm"})
            print("Payload sent. Waiting for response...")
            async for response in session.receive():
                print("Received response.", response)
                break
    except Exception as e:
        print(f"Error testing {model_name}: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test_live_api())

