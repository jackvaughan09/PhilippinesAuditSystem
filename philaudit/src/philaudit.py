import os
import pandas as pd
import PyPDF2 as p
from PyPDF2.errors import PdfReadError
import pdf2image
from tqdm import tqdm
import camelot
import warnings
from typing import List
import re
import sys

warnings.filterwarnings("ignore")

FILENAME_TARGET = ["Status", "Audit"]
TARGETS = [
    "status of implementation of prior years’ audit recommendations",
    "status of implementation of prior year's audit recommendations",
    "status of implementation of prior year’s recommendations",
    "status of implementation of prior years’ audit recommendation",
    "status of implementation of prior years’ recommendations",
]
CANON_HEADERS = [
    "audit observation",
    "recommendations",
    "references",
    "status of implementation",
    "reasons for partial/non-implementation",
    "management action",
]
FILTER_COLUMNS = [
    "references",
    "status of implementation",
]
BAD_NAMES = [
    ".docx",
    ".doc",
    "Part-1",
    "Certificate",
    "Part1",
    "Independent",
    "Part 1",
]


def clean(directory: str) -> None:
    """Remove duplicate files and specific unwanted files from a directory.
    Args:
        - directory (str): The directory to clean.
    """
    print(
        f"Removing unwanted files...\n\
    Current file count: {len(os.listdir(directory))}"
    )
    seen = set()
    for filename in tqdm(os.listdir(directory)):
        if filename not in seen:
            seen.add(filename)
        else:  # duplicate file
            print("duplicate file: " + filename)
            os.remove(os.path.join(directory, filename))
            continue

        if any(bad_name in filename for bad_name in BAD_NAMES):
            os.remove(os.path.join(directory, filename))
    print(f"Now there are: {len(os.listdir(directory))} files")


def text_normalize(s: str) -> str:
    # s = s.replace("\n", " ").replace("’", "'")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"([a-z])([A-Z])([a-z])", r"\1 \2\3", s)
    s = re.sub(r"([:,;.])(?!\s)", r"\1 ", s)
    s = s.lower().strip()
    return s


def page_contains_table(
    pdf_path: str, page_num: int, include_stream: bool = False
) -> bool:
    global removed_pages_tracker
    """
    Check if a specific page in a PDF file contains tables using the Camelot library.

    Args:
        - pdf_path (str): Path to the PDF file.
        - page_num (int): The 0-index page number to check for tables.
        - include_stream (bool): Whether to include stream tables in the check. Defaults to False.
    Returns:
        - bool: True if tables are detected, False otherwise.
    """
    stream_tables = False
    lattice_tables = False
    page_num += 1  # camelot is 1-indexed
    try:
        if len(camelot.read_pdf(pdf_path, flavor="lattice", pages=str(page_num))) > 0:
            return True
    except IndexError:
        return False
    except Exception:
        print(f"Error reading file {pdf_path} page {page_num} with lattice flavor")
        return False

    # TODO: skip stream tables for now, they are not as accurate
    # need to remove pages that only have the part 3 thing on it [MOSTLY DONE]
    # and pages that have no text content before trying to apply stream [DONE]

    if (not lattice_tables) and (include_stream == True):
        try:
            if (
                len(
                    camelot.read_pdf(
                        pdf_path,
                        flavor="stream",
                        pages=str(page_num),
                    )
                )
                > 0
            ):
                return True
        except Exception:
            print(f"Error reading file {pdf_path} page {page_num} with stream flavor")
            return False

    if not stream_tables and not lattice_tables:
        return False


def sequential_ranges(lst: List[int]) -> List[range]:
    if not lst:
        return []

    lst.sort()  # Make sure the list is sorted
    ranges = []
    start = lst[0]
    end = lst[0]
    i = 1

    while i < len(lst):  # Use < instead of <= to avoid IndexError
        if lst[i] - 1 != lst[i - 1]:
            end = lst[i - 1]  # Set end to the last element of the current range
            ranges.append(range(start, end + 1))
            start = lst[i]  # Update start to the new range's first element
        i += 1

    ranges.append(range(start, lst[-1] + 1))  # Append the last range

    return ranges


def remove_blank_pages_from_range(reader: p.PdfReader, page_rng: range) -> List[range]:
    """Remove pages that are mostly blank from a page range.

    Args:
       - reader (p.PdfFileReader): The PDF reader object for the file.
       - page_rng (range): A range object representing the 0-index PDF
       pages for the target tables.

    Returns:
       - rng (List[range]]): A list of ranges of pages that are not mostly blank.
    """
    try:
        mostly_blank = [
            i
            for i in page_rng
            if len(text_normalize(reader.pages[i].extract_text()).split(" ")) < 2
        ]
        good_indicies = [i for i in page_rng if i not in mostly_blank]
        if len(good_indicies) == 0:
            return None
        page_rng = sequential_ranges(good_indicies)
    except Exception as e:
        print(e)
    return page_rng


def find_toc(reader: p.PdfReader):
    try:
        toc_page = [
            i
            for i, page in enumerate(reader.pages)
            if "table of contents" in text_normalize(page.extract_text())
        ][0]
    except Exception:
        raise "No Table of Contents Found!"
    return toc_page


def detect_range_from_target_page(
    reader: p.PdfReader,
    start: int = 0,
) -> range:
    """Detect the page range of Part III tables from the target page.
    Finds the first page after `start` containing a target phrase
    (see `philaudit.TARGETS` variable).
    If a suitable target cannot be found, return original start to
    end of file.

    Args:
       - reader (p.PdfFileReader): The PDF reader object for the file.
       - start (int): The page number to start searching from.
       - pdf_url (str): The URL (Path) of the PDF file.

    Returns:
       - rng (range): The 0-index range of PDF pages with target tables
    """
    target_start = start
    end = len(reader.pages)
    for i, page in enumerate(reader.pages[start:]):
        i += start
        content = text_normalize(page.extract_text())
        if any([target for target in TARGETS if target in content]):
            target_start = i
            return range(target_start, end)
    return range(target_start, end)


def find_part3_range(reader: p.PdfReader, pdf_url: str) -> range:
    """
    Heuristic model for locating the page range of Part III in an Audit report.
    Args:
        - reader: (p.PdfReader): PyPDF2 PdfReader object for the PDF file
    Returns:
        - range: The 0-index range of PDF pages with target tables
                 If no Part III is found, returns None

    ### Description:
    - Worst case: if there is no Part III and no target page, return None
    - if there is no Part III, attempt target page detection
    - if there is Part III but no Part IV, return Part III to end
    - if both Part III and Part IV are present, return Part III to Part IV
    """
    contains_piii = []
    contains_piv = []

    for i, pg in enumerate(reader.pages):
        content = text_normalize(pg.extract_text())
        if "part iii" in content:
            contains_piii.append(i)
        if "part iv" in content:
            contains_piv.append(i)

    end = len(reader.pages)

    # Attempt to assign part 3 start and part 4 start
    try:
        part_3_start = int(contains_piii[-1])
        # When p3 is not the first page, we have to figure out if the start contains
        # a table to decide whether to include it or not
        if not page_contains_table(pdf_url, part_3_start):
            part_3_start += 1
    except IndexError:
        part_3_start = None
        pass
    try:
        part_4_start = int(contains_piv[-1])
    except IndexError:
        part_4_start = None
        pass

    # Edge case: part 3 starts before page 10 and pdf is longer than 50 pages
    if part_3_start is not None and part_3_start < 10 and end > 50:
        toc = find_toc(reader)
        rng = detect_range_from_target_page(reader, toc)
        return rng

    # Best case scenario: Have p3 and p4:
    if part_3_start is not None and part_4_start is not None:
        # if p4 comes before p3, return p3 to end
        if part_3_start > part_4_start:
            rng = range(part_3_start, end)
            return rng
        else:
            rng = range(part_3_start, part_4_start)
            return rng

    # If only p3 is present, return p3 to end
    if part_3_start is not None and part_4_start is None:
        rng = range(part_3_start, end)
        return rng

    # If no p3 or p4, attempt target page detection
    if part_3_start is None and part_4_start is None:
        try:
            rng = detect_range_from_target_page(reader)
            return rng
        except Exception:
            return None


def remove_pages_without_tables(page_ranges, pdf):
    table_ranges = []
    for rng in page_ranges:
        for pg in rng:
            if page_contains_table(pdf, pg):
                table_ranges.append(pg)
                continue
    return sequential_ranges(table_ranges)


def get_part3_pgs(pdf_dir, log_dir="./run_logs"):
    run_data = []
    print("Finding page ranges for Part III...", end=" ")
    for file in tqdm(os.listdir(pdf_dir)):
        # skip non-PDF files
        if not file.endswith(".pdf"):
            continue

        # attempt to read the PDF
        pdf_url = os.path.join(pdf_dir, file)
        try:
            reader = p.PdfReader(pdf_url)
        except PdfReadError as e:
            print(f"Error reading file {pdf_url}: {e}")
            continue

        # Find the page range of Part III
        part3_range = find_part3_range(reader, pdf_url)
        if not part3_range:
            continue

        # Remove pages that have very little text content
        # Because sometimes these types of pages are
        part3_range_list = remove_mostly_blank_pages_from_range(reader, part3_range)
        if not part3_range_list:
            continue

        part3_range_list = remove_pages_without_tables(part3_range_list, pdf_url)
        run_data.append((pdf_url, part3_range_list))

    # Save the data
    df = pd.DataFrame(run_data, columns=["file", "part3_range"])
    df["pg_count"] = df["part3_range"].apply(lambda x: sum([len(list(y)) for y in x]))
    df.to_csv(os.path.join(log_dir, "part3_pgs.csv"), index=False)
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


def pipe_data(
    pdf_dir: str = "./pdf", output_dir: str = "./images", log_dir: str = "./run_logs"
):
    clean(pdf_dir)
    data = get_part3_pgs(pdf_dir)
    data.to_csv(os.path.join(log_dir, "part3_pgs.csv"), index=False)
    print("Converting pages to images...")
    for _, row in tqdm(data.iterrows(), total=len(data)):
        convert_pages_to_bitmap(row, output_dir)
    print(f"All done! Now we have {len(os.listdir(output_dir))} images")


if __name__ == "__main__":
    pipe_data("./test_pipeline_pdfs/", "./test_pipeline_images/", "./test_logs/")
