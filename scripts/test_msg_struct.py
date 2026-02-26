from google import genai
from google.genai import types

def test_message_structure():
    msg = types.LiveClientMessage(
        tool_response=types.LiveClientToolResponse(
            function_responses=[
                types.FunctionResponse(
                    name="test",
                    id="123",
                    response={"result": "ok"}
                )
            ]
        )
    )
    print("Message dict:", msg.model_dump(exclude_none=True))

if __name__ == "__main__":
    test_message_structure()
