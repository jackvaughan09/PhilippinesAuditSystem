import os
import re
import shutil
import warnings
from typing import List, Union

import camelot
import fitz
import pandas as pd
import pdf2image
import PyPDF2 as p
from PyPDF2.errors import PdfReadError
from tabulate import tabulate
from tqdm import tqdm

warnings.filterwarnings("ignore")

TARGETS = [
    "status of implementation of prior years’ audit recommendations",
    "status of implementation of prior year's audit recommendations",
    "status of implementation of prior year’s recommendations",
    "status of implementation of prior years’ audit recommendation",
    "status of implementation of prior years’ recommendations",
    "status of implementation of prior year audit recommendations",
    "status of prior year’s recommendations",
    "status of implementation of prior years’ audit recommendati ons",
    "status of implementation of prior year’s audit recommendations",
    "status of implementation for prior year’s recommendations",
    "status of implementation of prior year’s audit recommendat ions",
    "status of implementation of prior years ’ audit recommendations",
    "status of implementation of prior years’saudit recommendations",
]
ANNEXES = ["annex", "annexes", "a n n e x", "a n n e x e s"]
# "annex" and "annexes" are too general to be used as p4 indicators reliably.
PART_4_INDICATORS = [
    "part iv",
    "iv. annex",
    "a n n e x e s",
    "annexes",
    "pa rt iv",
    "p art iv",
    "part i v",
    "part i v.",
    "part iv.",
    "part iv. annex",
]


def text_normalize(s: str) -> str:
    s = re.sub(r"\s+", " ", s)  # ensure single spaces
    s = re.sub(r"([a-z])([A-Z])([a-z])", r"\1 \2\3", s)  # split camelCase
    s = re.sub(r"([:,;.])(?!\s)", r"\1 ", s)  # add space after punctuation
    s = s.lower().strip()  # lowercase and strip
    pattern_iii = r"(?<![a-zA-Z])i *i *i(?![a-zA-Z])"
    s = re.sub(pattern_iii, "iii", s)  # fix roman numeral iii
    pattern_iv = r"(?<![a-zA-Z])i *v(?![a-zA-Z])"
    s = re.sub(pattern_iv, "iv", s)  # fix roman numeral iv
    return s


def page_contains_table(
    pdf_path: str, page_num: int, include_stream: bool = False
) -> bool:
    """
    Check if a specific page in a PDF file contains tables using the Camelot library.

    Args:
        - pdf_path (str): Path to the PDF file.
        - page_num (int): The 0-index page number to check for tables.
        - include_stream (bool): Whether to include stream tables in the check. Defaults to False.
    Returns:
        - bool: True if tables are detected, False otherwise.
    """
    page_num += 1  # camelot is 1-indexed
    if len(camelot.read_pdf(pdf_path, flavor="lattice", pages=str(page_num))) > 0:
        return True
    if include_stream == True:
        tables = camelot.read_pdf(pdf_path, flavor="stream", pages=str(page_num))
        if len(tables) > 0:
            return True
    return False


def sequential_ranges(lst: List[int]) -> List[range]:
    if not lst:
        return []
    lst.sort()  # Make sure the list is sorted
    ranges = []
    start = lst[0]
    end = lst[0]
    i = 1
    while i < len(lst):
        if lst[i] - 1 != lst[i - 1]:
            end = lst[i - 1]  # Set end to the last element of the current range
            ranges.append(range(start, end + 1))
            start = lst[i]  # Update start to the new range's first element
        i += 1
    ranges.append(range(start, lst[-1] + 1))  # Append the last range
    return ranges


def find_toc(reader: p.PdfReader):
    for i, page in enumerate(reader.pages):
        if "table of contents" in text_normalize(page.extract_text()):
            toc_page = i
            return toc_page
    return None


def clean_pg_content(reader, i):
    return text_normalize(reader.pages[i].extract_text())


def remove_cover_pages_from_range(reader: p.PdfReader, page_rng: range) -> range:
    i = page_rng[0]
    while (
        any([target in clean_pg_content(reader, i) for target in TARGETS])
        and len(clean_pg_content(reader, i)) < 75
    ):
        i += 1
    new_range = range(i, page_rng[-1] + 1)
    return new_range


def remove_annex_pages_from_end_of_range(reader: p.PdfReader, page_rng: range) -> range:
    # starting from end of range
    i = page_rng[-1]
    while any([a for a in ANNEXES if a in clean_pg_content(reader, i)]):
        i -= 1
    return range(page_rng[0], i + 1)


def remove_blank_pages_from_range(
    pdf: str, reader: p.PdfReader, page_rng: range
) -> List[range]:
    """Remove pages that are mostly blank from a page range.

    Args:
       - pdf (str): The local path to the PDF file.
       - reader (p.PdfFileReader): The PDF reader object for the file.
       - page_rng (range): A range object representing the 0-index PDF
       pages for the target tables.

    Returns:
       - rng (List[range]]): A list of ranges of pages that are not blank.
    """
    blank = [i for i in page_rng if len(clean_pg_content(reader, i).split(" ")) < 3]
    blank = [i for i in blank if not page_contains_table(pdf, i)]
    good_indicies = [i for i in page_rng if i not in blank]
    if len(good_indicies) == 0:
        return None
    # Condense the list to range objects with sequential pages
    page_rng = sequential_ranges(good_indicies)
    return page_rng


def remove_pages_without_tables(pdf, page_ranges):  # TODO is there something faster?
    table_ranges = []
    for rng in page_ranges:
        for pg in rng:
            if page_contains_table(pdf, pg, include_stream=True):
                table_ranges.append(pg)
                continue
    return sequential_ranges(table_ranges)


def detect_range_from_target_page(
    pdf: str,
    reader: p.PdfReader,
    start: int = 0,
    end: int = None,
) -> range:
    """Detect the page range of Part III tables from the target page.
    Finds the first page after `start` containing a target phrase
    (see `philaudit.TARGETS` variable).
    If a suitable target cannot be found, return original start to
    end of file.

    Args:
       - pdf (str): The path to the PDF to be read
       - reader (p.PdfFileReader): The PDF reader object for the file.
       - start (int): The 0-index page number to start searching from.
       - end (int): The 0-index page number to stop searching at.
    Returns:
       - rng (range): The 0-index range of PDF pages with target tables
    """
    target_start = start
    if not end:
        end = len(reader.pages)

    for i, page in enumerate(reader.pages[start:end]):
        i += start  # adjust for start
        content = text_normalize(page.extract_text())
        if any([target in content for target in TARGETS]):
            target_start = i
            if not page_contains_table(pdf, i):
                target_start += 1
                return range(target_start, end)
            else:
                return range(target_start, end)
    return range(target_start, end)


def assign_start_end_pages(reader):
    toc = find_toc(reader)
    if toc:
        start = toc + 1
        while any([x in clean_pg_content(reader, start) for x in PART_4_INDICATORS]):
            start += 1
    else:
        start = 0
    end = find_part4_start(reader, start)
    return start, end


def find_part4_start(reader: p.PdfReader, start) -> Union[int, None]:
    """
    Finds the starting page index of Part 4 in a PDF document,
    based on a list of predefined indicators.
    Args:
        - reader (PdfReader): A PyPDF2 PdfReader instance containing the
        pages of the PDF document.

    Returns:
        - int: The page index of the start of Part 4 in the document
        if found, otherwise None.

    Example:
        # Assuming the PDF file has been initialized as a PdfReader instance

        `part4_start = find_part4_start(pdf_reader)`
    """
    contains_piv = []
    for i, pg in enumerate(reader.pages[start:]):
        i += start  # account for start
        content = text_normalize(pg.extract_text())
        if any([x in content for x in PART_4_INDICATORS]):
            contains_piv.append(i)
    if len(contains_piv) > 0:
        # contains_piv = remove_sequences(contains_piv)
        return contains_piv[-1]
    else:
        return None


def get_part3_pgs(pdf_dir):
    run_data = []
    print("Finding page ranges for Part III...", end=" ")
    for file in tqdm(os.listdir(pdf_dir)):
        # skip non-PDF files
        if not file.endswith(".pdf"):
            continue

        # attempt to read the PDF
        pdf = os.path.join(pdf_dir, file)
        try:
            reader = p.PdfReader(pdf)
        except PdfReadError as e:
            print(f"Error reading file {pdf}: {e}")
            continue
        try:
            start, end = assign_start_end_pages(reader)
            part3_rng = detect_range_from_target_page(pdf, reader, start, end)
            part3_rng = remove_high_image_area_pages(pdf, part3_rng)
            part3_rng = remove_annex_pages_from_end_of_range(reader, part3_rng)
            part3_rng = remove_cover_pages_from_range(reader, part3_rng)
            page_ranges = remove_blank_pages_from_range(pdf, reader, part3_rng)
            page_ranges = remove_pages_without_tables(
                pdf, page_ranges
            )  # <-- Would love a faster way to do this...
        except Exception as e:
            run_data.append((pdf, ["Error:", e]))
            continue
        run_data.append((pdf, page_ranges))

    # Save the data
    df = pd.DataFrame(run_data, columns=["file", "part3_range"])
    return df


def convert_pages_to_bitmap(row: pd.Series, output_dir: str) -> None:
    """
    Convert specific pages from a PDF to bitmap images.

    :param row: pd.Series, contains the file path and page ranges to be converted
    :param output_dir: str, path to the directory where the output images will be saved
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pgs = []
    for rng in row.part3_range:
        pgs.extend(rng)
    images = pdf2image.convert_from_path(row.file)
    for pg_num in pgs:
        file = row.file.split("/")[-1]
        images[pg_num].save(
            os.path.join(output_dir, f"{file}_page_{pg_num + 1}.bmp"), "BMP"
        )


def image_area_ratio(page: fitz.Page) -> float:
    image_area = 0.0
    for img_info in page.get_image_info():
        bbox = img_info["bbox"]
        area = abs(bbox[2] - bbox[0]) * abs(bbox[3] - bbox[1])
        image_area += area
    return image_area / abs(page.rect)


def remove_high_image_area_pages(
    file_name: str, page_range: range, threshold: float = 0.5
) -> range:
    try:
        doc = fitz.open(file_name)
        i = page_range[-1]
        while image_area_ratio(doc[i]) > threshold:
            i -= 1
        doc.close()
        return range(page_range[0], i + 1)
    except (fitz.FileDataError, IndexError):
        print(f"Error: {file_name} is broken.")
        return None


def pipe_data(
    pdf_dir: str = "./pdf", output_dir: str = "./images", log_dir: str = "./run_logs"
):
    # Extract part 3 pages
    data = get_part3_pgs(pdf_dir, log_dir)

    # Save out errors
    errors = data.loc[data.part3_range.str.contains("Error")]
    errors.to_csv(os.path.join(log_dir, "errors.csv"), index=False)

    # Remove errors and save out data
    data = data.loc[~data.part3_range.str.contains("Error")]
    data = data.reset_index(drop=True)
    data.to_csv(os.path.join(log_dir, "part3_pgs.csv"), index=False)

    # Pipe the data to images
    print("Converting pages to images...")
    for _, row in tqdm(data.iterrows(), total=len(data)):
        convert_pages_to_bitmap(row, output_dir)
    print(f"All done! Now we have {len(os.listdir(output_dir))} images")


def get_pdf_image_area_ratio(file_name: str) -> float:
    """
    Calculate the ratio of the total image area to the total page area for a given PDF file.

    Args:
        - file_name (str): The path to the PDF file.

    Returns:
    float: The ratio of the total image area to the total page area. If the file cannot be opened,
    a value of 0.0 is returned.
    """
    total_page_area = 0.0
    total_image_area = 0.0

    try:
        doc = fitz.open(file_name)
    except fitz.FileDataError:
        print(f"Error: {file_name} is broken.")
        return 0.0

    for _, page in enumerate(doc):
        total_page_area += abs(page.rect)
        image_area = 0.0
        for img_info in page.get_image_info():
            bbox = img_info["bbox"]
            area = abs(bbox[2] - bbox[0]) * abs(bbox[3] - bbox[1])
            image_area += area
        total_image_area += image_area
    doc.close()
    return total_image_area / total_page_area


def isolate_high_image_area_ratio_pdfs(
    directory: str, to: str, threshold: float = 0.45
):
    """
    Isolate PDF files from a directory based on a given image area ratio threshold.

    Args:
    - directory (str): The path to the directory containing the PDF files.
    - to (str): The path to the destination directory where the PDF files with a high image area ratio will be moved.
    - threshold (float, optional): The image area ratio threshold. Files with an image area ratio greater than the threshold will be moved to the specified destination. Defaults to 0.45.

    Returns:
    None. PDF files with an image area ratio greater than the threshold are moved to the destination directory.
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        print(
            f"The specified directory '{directory}' does not exist or is not a directory."
        )
        return
    data = []
    headers = ["File Name", "Image Area Ratio"]
    for file_name in tqdm([f for f in os.listdir(directory) if f.endswith(".pdf")]):
        file_path = os.path.join(directory, file_name)
        if file_name.endswith(".pdf"):
            image_area_ratio = get_pdf_image_area_ratio(file_path)
            if image_area_ratio > threshold:
                data.append([file_name, image_area_ratio])
                shutil.move(file_path, to, file_name)
    print(tabulate(data, headers=headers, tablefmt="grid"))


# if __name__ == "__main__":
#     pipe_data("./pdf/", "./images/", "./output/")
