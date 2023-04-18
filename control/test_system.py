# System debugging entrypoint
# To use:
# 1. Set breakpoints at desired locations in whichever files
# you need.
# 2. Run this file from debugger

# NOTE: This always runs from root folder "PhilippinesAuditSystem"
# so the paths have to be relative to that dir ^

from datetime import date
import os
import shutil
from extract_all import extract_all
import logging
from logging_config import setup_logging


def get_new_wb_name():
    return "test_" + date.today().strftime("%B_%d_%Y")
    # return date.today().strftime("%B %d, %Y")


def mv_to_pdf_folder(di, ndi):
    for file in os.listdir(di):
        if "pdf" in os.path.splitext(file)[1].lower():
            shutil.move(
                os.path.join(di, file), os.path.join(ndi, os.path.basename(file))
            )
            logging.info(file, ndi)


if __name__ == "__main__":
    setup_logging()
    data_url = "data/pdf"
    df = extract_all(data_url)
    if not os.path.exists("data/xlsx"):
        os.mkdir("data/xlsx")
    logging.info("Exporting data to xlsx")
    df.to_excel("data/xlsx/" + get_new_wb_name() + ".xlsx")
    logging.info("All done!")
    logging.info(
        f"""Extracted observations from {df.source.nunique()} files.
Total observations: {df.shape[0]}"""
    )
