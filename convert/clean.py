import os
import sys
from shutil import rmtree
from zipfile import ZipFile

from tqdm import tqdm

FILENAME_TARGET = ["Status", "Audit"]
BAD_NAMES = [
    "Part-1",
    "Certificate",
    "Part1",
    "Independent",
    "Part 1",
    ".xlsx",
    "annexes",
    "Part4",
    "Part2",
    "Observations",
    "Annex",
    "annex",
    "Notes",
    "-FS",
    "_FS",
    "Part 1",
    "Table",
    "Errata",
    "Executive",
    "Summary",
    "Letter",
    "Cover",
    "AAPSI",
    "Action",
    "Annexes",
    "Part 2",
    "Part 4",
]
VALID_EXTENSIONS = [".pdf", ".docx", ".doc"]

# Keep track of the directories before unzipping
old_directories = set()


def get_directories(directory):
    return set(
        os.path.join(root, dir) for root, dirs, _ in os.walk(directory) for dir in dirs
    )


def unzip_in_place(root_dir):
    for root, dirs, files in tqdm(os.walk(root_dir)):
        for file in files:
            if file.endswith(".zip"):
                zip_path = os.path.join(root, file)
                try:
                    with ZipFile(zip_path, "r") as src:
                        src.extractall(root)
                except Exception as e:
                    print("Error unzipping file: " + zip_path)
                    print(e)
                    continue


def is_duplicate(filename, seen):
    if filename in seen:
        return True
    seen.add(filename)
    return False


def has_bad_name(filename):
    return any(bad_name in filename for bad_name in BAD_NAMES)


def has_target_and_valid_extension(filename):
    has_filename_target = any(
        target in os.path.splitext(filename)[0] for target in FILENAME_TARGET
    )
    file_extension = os.path.splitext(filename)[1]
    return has_filename_target and file_extension in VALID_EXTENSIONS


def clean_directory(directory: str) -> None:
    seen = set()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if is_duplicate(filename, seen):
            print("Duplicate file: " + filename)
            os.remove(file_path)
            continue

        if has_bad_name(filename) or not has_target_and_valid_extension(filename):
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif (
                file_path not in old_directories
            ):  # only remove newly created directories
                rmtree(file_path)
            continue


def main(root_dir):
    global old_directories
    old_directories = get_directories(root_dir)
    print("Unzipping files...")
    unzip_in_place(root_dir)
    # Clean each subdirectory of the root directory
    print("Cleaning up...")
    for root, dirs, files in tqdm(os.walk(root_dir)):
        for dir in dirs:
            clean_directory(os.path.join(root, dir))


if __name__ == "__main__":
    root_dir = sys.argv[1]
    main(root_dir)
