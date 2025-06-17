import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    parser = argparse.ArgumentParser(
        description="AI Agent CLI: Process a user prompt with optional verbose output."
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        'user_prompt',
        type=str,
        help='Prompt from the user'
    )

    args = parser.parse_args()

    # Load environment variables from .env file
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    # Prepare the AI client and model
    client = genai.Client(api_key=api_key)
    model = "gemini-2.0-flash-001"

    # Prepare to track the entire conversation
    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)]),
    ]

    # Generate content using the specified prompt
    response = client.models.generate_content(model=model, contents=messages)
    print(response.text)
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

if __name__ == "__main__":
    main()