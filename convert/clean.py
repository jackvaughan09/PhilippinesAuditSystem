#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLEAN.PY
Created on Thurs April 20, 2023 at 11:50 PM
@author: jackvaughan09
"""

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
]
VALID_EXTENSIONS = [".pdf", ".docx", ".doc"]


def unzip(zipped, unzipped):
    z_list = [
        os.path.join(zipped, f)
        for f in os.listdir(zipped)
        if os.path.isfile(os.path.join(zipped, f)) and f[0] != "."
    ]
    for z in z_list:
        with ZipFile(z, "r") as src:
            src.extractall(unzipped)


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
    """Remove duplicate files, specific unwanted files, and junk files from a directory.
    Args:
        - directory (str): The directory to clean.
    """
    print(
        f"Removing unwanted files...\n\
    Current file count: {len(os.listdir(directory))}"
    )
    seen = set()
    for filename in tqdm(os.listdir(directory)):
        file_path = os.path.join(directory, filename)

        if is_duplicate(filename, seen):
            print("Duplicate file: " + filename)
            os.remove(file_path)
            continue

        if has_bad_name(filename):
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                rmtree(file_path)
            continue

        if not has_target_and_valid_extension(filename):
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                rmtree(file_path)
            continue

    print(f"Now there are: {len(os.listdir(directory))} files")


def main(zipped_dir, unzipped_dir):
    unzip(zipped_dir, unzipped_dir)
    clean_directory(unzipped_dir)


if __name__ == "__main__":
    zipped_dir = sys.argv[1]
    unzipped_dir = sys.argv[2]
    main(zipped_dir, unzipped_dir)
