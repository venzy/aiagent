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

    # System prompt (hard coded for now)
    system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
The root directory is the working directory, and is represented by a dot (.) in your function calls.
"""

    # Declare our functions
    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                ),
            },
        ),
    )

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
        ]
    )

    # Generate content using the specified prompt
    response = client.models.generate_content(
        model=model,
        contents=messages,
        config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
        )
    
    for function_call_part in response.function_calls:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")

    #print(response.text)

    # Metrics - may be used for more than verbose output
    prompt_tokens = response.usage_metadata.prompt_token_count
    response_tokens = response.usage_metadata.candidates_token_count

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens:{response_tokens}")

if __name__ == "__main__":
    main()