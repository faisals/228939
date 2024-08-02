import os
import pyperclip

def is_text_file(file_path):
    text_file_extensions = ['.py', '.txt', '.html', '.css', '.md', '.js']
    return any(file_path.endswith(ext) for ext in text_file_extensions)

def get_file_paths_and_content(root_dir):
    excluded_files = ['README.md', 'leetcoder.db', 'progress.txt']
    file_data = []
    for root, dirs, files in os.walk(root_dir):
        # Exclude __pycache__ directory
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            # Exclude specific files
            if file in excluded_files:
                continue
            file_path = os.path.join(root, file)
            if is_text_file(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                file_data.append(f"File: {file_path}\nContent:\n{file_content}\n")
    return file_data

def copy_to_clipboard(data):
    pyperclip.copy("\n".join(data))

if __name__ == "__main__":
    current_directory = os.getcwd()
    file_data = get_file_paths_and_content(current_directory)
    copy_to_clipboard(file_data)
    print("All file paths and contents copied to clipboard.")
