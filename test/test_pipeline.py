import os
from typing import List

import PyPDF2 as p
import pytest
from test_cases import test_cases
from philaudit import PhilDocAnalyzer

TEST_PDF_DIR = "../pdf/"

files = [file.lower() for file in os.listdir(TEST_PDF_DIR) if file.endswith(".pdf")]


def is_test_case(file: str) -> bool:
    return any([case in file for case in test_cases.keys()])


def case_matcher(file: str) -> str:
    for case in test_cases.keys():
        if case in file:
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
    doc = PhilDocAnalyzer(pdf)
    assert doc.target_range == should_be


# def test_convert_images_from_ranges():
#     pass
