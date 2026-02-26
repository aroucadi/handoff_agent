import asyncio
import os
from google import genai
from google.genai.types import LiveConnectConfig, Modality

async def test_receive_protocol():
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    model_id = "models/gemini-2.5-flash-native-audio-latest"
    
    config = LiveConnectConfig(response_modalities=[Modality.AUDIO])
    
    print("Testing: session.receive() protocol...")
    try:
        async with client.aio.live.connect(model=model_id, config=config) as session:
            # Try async with (should fail if it's the bug)
            print("Trying: async with session.receive()...")
            try:
                async with session.receive() as stream:
                    print("SUCCESS: async with worked (unexpected)")
            except Exception as e:
                print(f"EXPECTED FAILURE: async with failed - {e}")
                
            # Try async for (should work)
            print("Trying: async for response in session.receive()...")
            # We just want to see if it starts iterating or errors on the call
            it = session.receive().__aiter__()
            print("SUCCESS: obtained aiter from session.receive()")
            
    except Exception as e:
        print(f"Global error: {e}")

if __name__ == "__main__":
    asyncio.run(test_receive_protocol())
