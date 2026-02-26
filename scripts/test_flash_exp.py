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
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
    # v1alpha is needed for gemini-2.0-flash-exp live api sometimes, or v1beta handles it.
    
    model_name = "models/gemini-2.0-flash-exp"
    
    try:
        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO]
        )
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"Connected to {model_name}")
            print(f"Sending text with send_realtime_input...")
            await session.send_realtime_input(text="Hello, how are you?")
            
            async for response in session.receive():
                if response.server_content and response.server_content.turn_complete:
                    print("Turn complete")
                    break
    except Exception as e:
        print(f"Error: {repr(e)}")


if __name__ == "__main__":
    asyncio.run(test_live_api())

