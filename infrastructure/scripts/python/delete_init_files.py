import os

def delete_init_py_files(directory):
    """
    Recursively delete all __init__.py files in the specified directory and its subdirectories.

    :param directory: The base directory to search for __init__.py files.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "__init__.py":
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")

if __name__ == "__main__":
    # Specify the directory you want to start the search from
    base_directory = r"C:\path\to\your\folder"

    delete_init_py_files(base_directory)
    print("All __init__.py files have been deleted.")
