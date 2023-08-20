import os

# List of file names to search for
file_names = ['urls.py', 'models.py', 'views.py', 'serializers.py']
ignored_folders = ['.my_env', 'my_env']

def find_files(directory):
    found_files = []
    for root, dirs, files in os.walk(directory):
        # Exclude ignored folders
        dirs[:] = [d for d in dirs if d not in ignored_folders]
        for file in files:
            if file in file_names:
                found_files.append(os.path.join(root, file))
    return found_files

def compile_files_into_prompt(files):
    with open('prompt.txt', 'w') as prompt_file:
        for file_path in files:
            relative_path = os.path.relpath(file_path, directory)
            prompt_file.write(f"==== {relative_path} ====\n\n")
            with open(file_path, 'r') as source_file:
                prompt_file.write(source_file.read())
            prompt_file.write('\n\n')

if __name__ == '__main__':
    directory = input("Enter the root directory to start crawling: ")
    if not os.path.exists(directory):
        print("Directory does not exist.")
    else:
        found_files = find_files(directory)
        compile_files_into_prompt(found_files)
        print("Compilation complete. Check prompt.txt.")
