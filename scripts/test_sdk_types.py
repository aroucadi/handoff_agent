from google import genai
from google.genai import types

def test_types():
    print("FunctionCall fields:", dir(types.FunctionCall))
    print("FunctionResponse fields:", dir(types.FunctionResponse))
    
    fc = types.FunctionCall(name="test", args={"x": 1}, id="123")
    print(f"FC id: {fc.id}")
    
    fr = types.FunctionResponse(name="test", id="123", response={"result": "ok"})
    print(f"FR id: {fr.id}")

if __name__ == "__main__":
    test_types()
