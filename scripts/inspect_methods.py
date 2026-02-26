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
    
    try:
        live_config = LiveConnectConfig(response_modalities=[Modality.AUDIO])
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            sig_tool = inspect.signature(session.send_tool_response) if hasattr(session, 'send_tool_response') else 'Not Found'
            sig_realrt = inspect.signature(session.send_realtime_input) if hasattr(session, 'send_realtime_input') else 'Not Found'
            sig_content = inspect.signature(session.send_client_content) if hasattr(session, 'send_client_content') else 'Not Found'
            
            print(f"send_tool_response: {sig_tool}")
            print(f"send_realtime_input: {sig_realrt}")
            print(f"send_client_content: {sig_content}")
            
    except Exception as e:
        print(f"Error: {repr(e)}")


if __name__ == "__main__":
    asyncio.run(test_live_api())

