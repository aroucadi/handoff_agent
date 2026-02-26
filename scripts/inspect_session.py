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
import inspect

async def test_live_api():
    api_key_bytes = subprocess.check_output(["gcloud.cmd", "secrets", "versions", "access", "latest", "--secret=gemini-api-key", "--project=synapse-488201"])
    api_key = api_key_bytes.decode('utf-8').strip()
    
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    
    print(f"\n--- Testing API methods ---")
    try:
        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
        )
        
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"Dir of session: {[m for m in dir(session) if not m.startswith('_')]}")
            
            if hasattr(session, 'send_tool_response'):
                sig = inspect.signature(session.send_tool_response)
                print(f"send_tool_response signature: {sig}")
            if hasattr(session, 'send'):
                sig = inspect.signature(session.send)
                print(f"send signature: {sig}")
            
    except Exception as e:
        print(f"Error: {repr(e)}")


if __name__ == "__main__":
    asyncio.run(test_live_api())

