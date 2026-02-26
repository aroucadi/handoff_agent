import asyncio
import os
import sys
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
    api_key = "AIzaSyBKJl-jMO9GA_gp77l9f7DnfwLIdUj3PMo"
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    
    try:
        declarations = [
            FunctionDeclaration(
                name="read_index",
                description="Read the index node.",
                parameters={"type": "object", "properties": {"client_id": {"type": "string"}}, "required": ["client_id"]},
            )
        ]

        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            system_instruction=Content(parts=[Part.from_text(text="Execute read_index. client_id='123'")]),
            tools=[Tool(function_declarations=declarations)]
        )
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"Connected to {model_name}")
            kickoff = "SYSTEM_EVENT: Execute 'read_index' tool immediately. client_id='123'."
            await session.send_realtime_input(text=kickoff)
            
            async for response in session.receive():
                if response.tool_call:
                    fc = response.tool_call.function_calls[0]
                    print(f"Got tool call: {fc.name}")
                    
                    # Create a HUGE fake response string (e.g. 150KB)
                    huge_result = "data " * 50000 
                    print(f"Sending huge tool response ({len(huge_result)} bytes)...")
                    
                    await session.send_tool_response(
                        function_responses=[FunctionResponse(name=fc.name, id=fc.id, response={"result": huge_result})]
                    )
                
                if response.server_content and response.server_content.turn_complete:
                    print("Turn complete")
                    break

    except Exception as e:
        print(f"Error testing: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test_live_api())

