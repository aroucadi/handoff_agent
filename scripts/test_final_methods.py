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
    Tool,
    FunctionResponse
)

async def test_live_api():
    api_key_bytes = subprocess.check_output(["gcloud.cmd", "secrets", "versions", "access", "latest", "--secret=gemini-api-key", "--project=synapse-488201"])
    api_key = api_key_bytes.decode('utf-8').strip()
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    
    try:
        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            tools=[Tool(function_declarations=[FunctionDeclaration(name="t1", description="test")])]
        )
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"Connected to {model_name}")
            print(f"Sending text with send_realtime_input...")
            await session.send_realtime_input(text="Hello, call t1")
            
            async for response in session.receive():
                if response.tool_call:
                    fc = response.tool_call.function_calls[0]
                    print(f"Got tool call {fc.name}")
                    print("Sending tool response with send_tool_response...")
                    await session.send_tool_response(
                        function_responses=[
                            FunctionResponse(name=fc.name, id=fc.id, response={"res": "ok"})
                        ]
                    )
                if response.server_content and response.server_content.turn_complete:
                    print("Turn complete")
                    break
    except Exception as e:
        print(f"Error: {repr(e)}")


if __name__ == "__main__":
    asyncio.run(test_live_api())

