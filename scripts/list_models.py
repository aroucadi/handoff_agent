import asyncio
import os
import subprocess
from google import genai

async def test_live_api():
    api_key_bytes = subprocess.check_output(["gcloud.cmd", "secrets", "versions", "access", "latest", "--secret=gemini-api-key", "--project=synapse-488201"])
    api_key = api_key_bytes.decode('utf-8').strip()
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    
    print("Listing models with supported actions...")
    models = client.models.list()
    for m in models:
        actions = []
        if getattr(m, 'supported_generation_methods', None):
            actions = m.supported_generation_methods
        if 'bidiGenerateContent' in actions:
            print(f"- {m.name}")

if __name__ == "__main__":
    asyncio.run(test_live_api())

