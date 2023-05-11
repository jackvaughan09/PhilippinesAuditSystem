import os
from typing import List

import PyPDF2 as p
import pytest

import philaudit as pa
from test_cases import test_cases

TEST_PDF_DIR = ""

files = [file for file in os.listdir(TEST_PDF_DIR) if file.endswith(".pdf")]


def is_test_case(file: str) -> bool:
    return any([case in file.lower() for case in test_cases.keys()])


def case_matcher(file: str) -> str:
    for case in test_cases.keys():
        if case in file.lower():
            return test_cases[case]
    # raise ValueError("No test case found for file: " + file)


def load_test_cases():
    for file in files:
        if is_test_case(file):
            target_range = case_matcher(file)
            pdf = TEST_PDF_DIR + file
            yield (pdf, target_range)
        else:
            continue


@pytest.mark.parametrize(
    "pdf, should_be",
    list(load_test_cases()),
)
def test_target_page_detection(pdf, should_be):
    reader = p.PdfReader(pdf)
    start, end = pa.assign_start_end_pages(reader)
    part3_rng = pa.detect_range_from_target_page(pdf, reader, start, end)
    part3_rng = pa.remove_high_image_area_pages(pdf, part3_rng)
    part3_rng = pa.remove_annex_pages_from_end_of_range(reader, part3_rng)
    part3_rng = pa.remove_cover_pages_from_range(reader, part3_rng)
    page_ranges = pa.remove_blank_pages_from_range(pdf, reader, part3_rng)
    page_ranges = pa.remove_pages_without_tables(
        pdf, page_ranges
    )  # <-- Would love a faster way to do this...
    assert page_ranges == should_be


# def test_convert_images_from_ranges():
#     pass
