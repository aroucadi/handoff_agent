import asyncio
import os
from google import genai
from google.genai.types import LiveConnectConfig, Modality, Tool, FunctionDeclaration

async def test_native_audio_tools():
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    model_id = "models/gemini-2.5-flash-native-audio-latest"
    
    # Define a simple tool
    tools = [Tool(function_declarations=[
        FunctionDeclaration(
            name="get_weather",
            description="Get the weather",
            parameters={"type": "object", "properties": {"location": {"type": "string"}}},
        )
    ])]
    
    config = LiveConnectConfig(
        response_modalities=[Modality.AUDIO],
        tools=tools
    )
    
    print(f"Testing tools with {model_id}...")
    try:
        async with client.aio.live.connect(model=model_id, config=config) as session:
            print("Connected successfully with tools.")
            
            # Send a kickoff text to trigger the tool
            print("Sending text kickoff...")
            await session.send(input="What is the weather in London?", end_of_turn=True)
            
            async for response in session.receive():
                if response.tool_call:
                    print(f"SUCCESS: Tool call received: {response.tool_call}")
                    break
                if response.server_content:
                    print(f"Received server content (Audio/Text)")
                    # If we get audio/text but no tool call, it might be ignoring the tool
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(test_native_audio_tools())
