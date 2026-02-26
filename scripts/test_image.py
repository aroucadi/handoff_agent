import asyncio
import os
import subprocess
from google import genai
from google.genai.types import (
    LiveConnectConfig,
    Content,
    Part,
    FunctionDeclaration,
    Modality,
    Tool
)

async def test_live_api():
    api_key_bytes = subprocess.check_output(["gcloud.cmd", "secrets", "versions", "access", "latest", "--secret=gemini-api-key", "--project=synapse-488201"])
    api_key = api_key_bytes.decode('utf-8').strip()
    
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    
    print(f"\n--- Testing Model: {model_name} ---")
    try:
        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            system_instruction=Content(parts=[Part.from_text(text="Audio.")]),
        )
        
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print("Connected. Sending image...")
            # Send a fake jpeg
            await session.send(input={"data": b"\xFF\xD8\xFF\xE0" + b"\x00"*10, "mime_type": "image/jpeg"})
            print("Image sent. Waiting...")
            async for response in session.receive():
                print("Got response")
                break
    except Exception as e:
        print(f"Error testing {model_name}: {repr(e)}")


if __name__ == "__main__":
    asyncio.run(test_live_api())

