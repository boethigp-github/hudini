import os
import shutil


def duplicate_files(input_dir, output_dir, duplication_factor=10):
    """
    Duplicates files in the input directory and saves them in the output directory.

    Parameters:
        input_dir (str): The directory containing the original files.
        output_dir (str): The directory where duplicated files will be saved.
        duplication_factor (int): Number of times to duplicate each file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    files = os.listdir(input_dir)
    if not files:
        print("No files found in the input directory!")
        return

    print(f"Duplicating {len(files)} files from '{input_dir}' to '{output_dir}' with a factor of {duplication_factor}.")

    for file in files:
        input_file_path = os.path.join(input_dir, file)
        if not os.path.isfile(input_file_path):
            continue

        file_name, file_ext = os.path.splitext(file)
        for i in range(duplication_factor):
            new_file_name = f"{file_name}_copy{i + 1}{file_ext}"
            new_file_path = os.path.join(output_dir, new_file_name)
            shutil.copy2(input_file_path, new_file_path)
            print(f"Created: {new_file_path}")

    print("Duplication completed.")


# Configure your paths and duplication factor
if __name__ == "__main__":
    INPUT_DIR = r"/server/app/utils/finetuning/documentation_llm/trainingsdaten/routers"
    OUTPUT_DIR = r"/server/app/utils/finetuning/documentation_llm/trainingsdaten/duplicated"
    DUPLICATION_FACTOR = 100

    duplicate_files(INPUT_DIR, OUTPUT_DIR, DUPLICATION_FACTOR)
