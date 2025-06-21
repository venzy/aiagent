import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions import get_files_info, get_file_content, run_python_file, write_file

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
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

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

    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Retrieves the content of a specified file, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the file to retrieve, relative to the working directory.",
                ),
            },
        ),
    )

    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Executes a Python file in the working directory and returns its output.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the Python file to execute, relative to the working directory.",
                ),
            },
        ),
    )

    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Writes content to a specified file, creating it if it does not exist, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the file to write to, relative to the working directory.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="The content to write to the file.",
                ),
            },
        ),
    )

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    # Generate content using the specified prompt
    response = client.models.generate_content(
        model=model,
        contents=messages,
        config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
        )
    
    for function_call_part in response.function_calls:
        function_call_result = call_function(function_call_part, verbose=args.verbose)
        function_response = function_call_result.parts[0].function_response.response
        if args.verbose:
            print(f"-> {function_response}")

    #print(response.text)

    # Metrics - may be used for more than verbose output
    prompt_tokens = response.usage_metadata.prompt_token_count
    response_tokens = response.usage_metadata.candidates_token_count

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens:{response_tokens}")


def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f"Calling function: {function_call_part.name}")
    
    # For now, hard-code working directory
    working_directory = "./calculator"
    args = dict(function_call_part.args)
    args["working_directory"] = working_directory
    
    match function_call_part.name:
        case "get_files_info":
            function_result = get_files_info.get_files_info(**function_call_part.args)
        case "get_file_content":
            function_result = get_file_content.get_file_content(**function_call_part.args)
        case "run_python_file":
            function_result = run_python_file.run_python_file(**function_call_part.args)
        case "write_file":
            function_result = write_file.write_file(**function_call_part.args)
        case _:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_call_part.name,
                        response={"error": f"Unknown function: {function_call_part.name}"},
                    )
                ],
            )

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": function_result},
            )
        ],
    )

if __name__ == "__main__":
    main()