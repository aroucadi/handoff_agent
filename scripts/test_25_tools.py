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
    api_key = "AIzaSyBKJl-jMO9GA_gp77l9f7DnfwLIdUj3PMo"
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    
    try:
        declarations = [
            FunctionDeclaration(
                name="read_index",
                description="Read the index/table-of-contents node for a skill graph layer.",
                parameters={
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "layer": {"type": "string", "enum": ["client", "product", "industry"]},
                    },
                    "required": ["client_id"],
                },
            ),
            FunctionDeclaration(
                name="follow_link",
                description="Navigate to a specific node in the skill graph.",
                parameters={
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "node_id": {"type": "string"},
                        "sections_only": {"type": "boolean"},
                    },
                    "required": ["client_id", "node_id"],
                },
            ),
            FunctionDeclaration(
                name="search_graph",
                description="Semantic search across the skill graph. ",
                parameters={
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "query": {"type": "string"},
                    },
                    "required": ["client_id", "query"],
                },
            ),
        ]

        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            system_instruction=Content(parts=[Part.from_text(text="Execute read_index. layer='client', client_id='123'")]),
            tools=[Tool(function_declarations=declarations)]
        )
        async with client.aio.live.connect(model=model_name, config=live_config) as session:
            print(f"Connected to {model_name}")
            킥off = ("SYSTEM_EVENT: Execute the 'read_index' tool immediately. client_id='123', layer='client'. "
                      "After receiving the tool result, greet the user ALOUD.")
            await session.send_realtime_input(text=킥off)
            
            async for response in session.receive():
                if response.server_content and response.server_content.model_turn:
                    for part in response.server_content.model_turn.parts:
                        if part.text: print(part.text)
                
                if response.tool_call:
                    fc = response.tool_call.function_calls[0]
                    print(f"Got tool call: {fc.name}({fc.args})")
                    await session.send_tool_response(
                        function_responses=[FunctionResponse(name=fc.name, id=fc.id, response={"result": "data"})]
                    )
                
                if response.server_content and response.server_content.turn_complete:
                    print("Turn complete")
                    break

    except Exception as e:
        print(f"Error testing: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test_live_api())

