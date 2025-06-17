import os

def get_files_info(working_directory, directory=None):
    if directory is None:
        directory = working_directory
    abs_directory = os.path.abspath(os.path.join(working_directory, directory))
    abs_working_directory = os.path.abspath(working_directory)
    if not abs_directory.startswith(abs_working_directory):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(abs_directory):
        return f'Error: "{directory}" is not a directory'
    try:
        entries = os.listdir(abs_directory)
        lines = []
        for entry in sorted(entries):
            entry_path = os.path.join(abs_directory, entry)
            is_dir = os.path.isdir(entry_path)
            file_size = os.path.getsize(entry_path)
            lines.append(f"- {entry}: file_size={file_size} bytes, is_dir={is_dir}")
        return "\n".join(lines)
    except Exception as e:
        return f'Error: {e}'
