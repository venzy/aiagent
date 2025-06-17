import os, sys
from dotenv import load_dotenv
from google import genai

def main():
    # Parse command line arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py <prompt>")
        sys.exit(1)

    prompt = sys.argv[1]

    # Load environment variables from .env file
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    # Prepare the AI client and model
    client = genai.Client(api_key=api_key)
    model = "gemini-2.0-flash-001"

    # Generate content using the specified prompt
    response = client.models.generate_content(model=model, contents=prompt)
    print(response.text)
    print("Prompt tokens:", response.usage_metadata.prompt_token_count)
    print("Response tokens:", response.usage_metadata.candidates_token_count)

main()