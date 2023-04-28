#!/usr/bin/env python3A
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

FILENAME_TARGET = ["Status", "Audit"]


def unzip(zipped, unzipped):
    z_list = [
        os.path.join(zipped, f)
        for f in os.listdir(zipped)
        if os.path.isfile(os.path.join(zipped, f)) and f[0] != "."
    ]
    for z in z_list:
        with ZipFile(z, "r") as src:
            src.extractall(unzipped)


def remove_junk(unzipped_dir):
    # Remove all files that are not .pdf or .docx
    uz_list = [os.path.join(unzipped_dir, f) for f in os.listdir(unzipped_dir)]
    for f in uz_list:
        has_filename_target = any(
            [target in os.path.splitext(f)[0] for target in FILENAME_TARGET]
        )
        is_pdf = bool(os.path.splitext(f)[1] == ".pdf")
        is_doc = bool(os.path.splitext(f)[1] in [".docx", ".doc"])
        if is_doc and has_filename_target:
            continue
        elif is_pdf and has_filename_target:
            continue
        elif os.path.isfile(f):
            os.remove(f)
        else:
            rmtree(f)


if __name__ == "__main__":
    zipped_dir = sys.argv[1]
    unzipped_dir = sys.argv[2]
    unzip(zipped_dir, unzipped_dir)
    remove_junk(unzipped_dir)
