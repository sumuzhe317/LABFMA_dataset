import os


def remove_substring(original_string, substring_to_remove):
    new_string = original_string.replace(substring_to_remove, '')
    return new_string

def remove_temp_files(directory_path):
    files = os.listdir(directory_path)
    for file_name in files:
        if not file_name.endswith(".tex"):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)