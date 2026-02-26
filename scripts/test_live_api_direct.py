import asyncio
import os
import subprocess
from google import genai
from google.genai.types import (
    LiveConnectConfig,
    PrebuiltVoiceConfig,
    VoiceConfig,
    SpeechConfig,
    Content,
    Part,
    FunctionDeclaration,
    Modality,
    Tool,
    LiveClientContent,
    LiveClientToolResponse,
    FunctionResponse
)
import json

async def test_live_api():
    api_key_bytes = subprocess.check_output(["gcloud.cmd", "secrets", "versions", "access", "latest", "--secret=gemini-api-key", "--project=synapse-488201"])
    api_key = api_key_bytes.decode('utf-8').strip()
    
    if not api_key:
        print("Missing API KEY")
        return
        
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    
    print(f"\n--- Testing Model: {model_name} ---")
    try:
        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            system_instruction=Content(parts=[Part.from_text(text="Always reply with AUDIO.")]),
            tools=[
                Tool(function_declarations=[
                    FunctionDeclaration(name="test_tool", description="test tool to see if it works")
                ])
            ]
        )
        
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"[{model_name}] Connected successfully.")
            
            print(f"[{model_name}] Sending text...")
            await session.send(input="Hello, please use the test_tool explicitly now.", end_of_turn=True)
            
            print(f"[{model_name}] Waiting for response...")
            async for response in session.receive():
                if response.server_content and response.server_content.model_turn:
                    print(f"[{model_name}] Got turn content")
                if response.tool_call:
                    fc = response.tool_call.function_calls[0]
                    print(f"[{model_name}] Got tool call: {fc.name} with id {fc.id}")
                    
                    # Test tool response structure
                    print(f"[{model_name}] Sending tool response...")
                    
                    tool_resp = LiveClientContent(
                        tool_response=LiveClientToolResponse(
                            function_responses=[
                                FunctionResponse(
                                    name=fc.name,
                                    id=fc.id,
                                    response={"result": "success"}
                                )
                            ]
                        )
                    )
                    await session.send(input=tool_resp)
                if response.server_content and response.server_content.turn_complete:
                    print(f"[{model_name}] Turn complete")
                    break
    except Exception as e:
        print(f"Error testing {model_name}: {repr(e)}")


if __name__ == "__main__":
    asyncio.run(test_live_api())

