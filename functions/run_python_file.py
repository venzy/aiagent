import os
import subprocess

def run_python_file(working_directory, file_path):
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    abs_working_directory = os.path.abspath(working_directory)
    
    if not abs_file_path.startswith(abs_working_directory):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(abs_file_path):
        return f'Error: File "{file_path}" not found.'
    
    if not abs_file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        processResults = subprocess.run(args=['python3', abs_file_path],
                                    cwd=abs_working_directory,
                                    capture_output=True,
                                    timeout=30)
        result = []
        stderr = processResults.stderr.decode('utf-8').strip()
        stdout = processResults.stdout.decode('utf-8').strip()
        if len(stderr) == 0 and len(stdout) == 0:
            result.append('No output produced.')
        if len(stdout) > 0:
            result.append(f'STDOUT:{stdout}')
        if len(stderr) > 0:
            result.append(f'STDERR:{stderr}')
        if processResults.returncode != 0:
            result.append(f'Process exited with code {processResults.returncode}')
        
        return '\n'.join(result)

    except Exception as e:
        return f'Error: executing Python file: {e}'
 