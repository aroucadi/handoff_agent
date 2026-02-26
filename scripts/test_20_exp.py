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
    
    # Let's test if gemini-2.0-flash-exp works, maybe only the standard 2.0-flash was blocked
    model_name = "models/gemini-2.0-flash-exp"
    
    try:
        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            tools=[Tool(function_declarations=[FunctionDeclaration(name="test", description="test tool")])]
        )
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"Connected to {model_name}")
            print(f"Sending audio chunk to see if it causes 1008...")
            # Send 1 second of silence
            audio_bytes = b'\x00' * 32000
            await session.send_realtime_input(audio={"data": audio_bytes, "mime_type": "audio/pcm;rate=16000"})
            
            async for response in session.receive():
                pass
    except Exception as e:
        print(f"Error testing {model_name}: {repr(e)}")


if __name__ == "__main__":
    asyncio.run(test_live_api())

