import google.generativeai as genai
import os

def test_gemini_connection():
    try:
        # Configure the API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment variables")
            return
        
        genai.configure(api_key=api_key)
        
        # Try to list available models
        print("Attempting to list available models...")
        models = genai.list_models()
        print("\nAvailable models:")
        for model in models:
            print(f"- {model.name}")
        
        # Try a simple generation
        print("\nAttempting a simple text generation...")
        model = genai.GenerativeModel('gemini-1.0-pro')
        response = model.generate_content("Say hello!")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_gemini_connection() 