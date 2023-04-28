import os
import pandas as pd
import PyPDF2 as p
from PyPDF2.errors import PdfReadError
import pdf2image
from tqdm import tqdm
import camelot
import warnings
from typing import List, Tuple
import re

no_table_pages = []
removed_pages_tracker = []
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
    """Remove duplicate files and common unwanted files from a directory.
    Args:
        directory (str): The directory to clean.
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
            os.remove(directory + filename)
            continue

        if any(bad_name in filename for bad_name in BAD_NAMES):
            os.remove(directory + filename)
    print(f"Now there are: {len(os.listdir(directory))} files")


def text_normalize(s: str) -> str:
    s = s.replace("\n", " ")
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
        pdf_path (str): Path to the PDF file.
        page_num (int): The page number to check for tables.
        include_stream (bool): Whether to include stream tables in the check. Defaults to False.
    Returns:
        bool: True if tables are detected, False otherwise.
    """
    stream_tables = []
    lattice_tables = []
    try:
        lattice_tables = camelot.read_pdf(
            pdf_path, flavor="lattice", pages=str(page_num)
        )
    except Exception:
        print(f"Error reading file {pdf_path} page {page_num} with lattice flavor")
        _store_temp_data(
            reader=None,
            page=page_num,
            kind="no_table",
            title=pdf_path.split("/")[-1],
            author="",
        )
        return False

    # TODO: skip stream tables for now, they are not as accurate
    # need to remove pages that only have the part 3 thing on it [MOSTLY DONE]
    # and pages that have no text content before trying to apply stream [DONE]

    if len(lattice_tables) == 0 and include_stream:
        stream_tables = camelot.read_pdf(
            pdf_path,
            flavor="stream",
            pages=str(page_num),
        )

    if len(stream_tables) == 0 and len(lattice_tables) == 0:
        _store_temp_data(
            reader=None,
            page=page_num,
            kind="no_table",
            title=pdf_path.split("/")[-1],
            author="",
        )
    return len(stream_tables) > 0 or len(lattice_tables) > 0


def sequential_ranges(lst: List[int]) -> List[Tuple[int, int]]:
    """Convert a list of numbers into a list of tuples representing sequential ranges."""
    ranges = []
    start = lst[0]
    for i in range(1, len(lst)):
        if lst[i] != lst[i - 1] + 1:
            ranges.append((start, lst[i - 1]))
            start = lst[i]
    ranges.append((start, lst[-1]))
    return ranges


def remove_mostly_blank_pages_from_range(
    reader: p.PdfReader, page_rng: Tuple[int, int]
) -> List[Tuple[int, int]]:
    """Remove pages that are mostly blank from a page range.

    Args:
        reader (p.PdfFileReader): The PDF reader object for the file.
        page_rng (Tuple[int, int]): A tuple with the start and end page numbers.

    Returns:
        rng (List[Tuple[int, int]]): A list of tuples with the start and end page numbers.
    """

    rng = range(page_rng[0], page_rng[1] + 1)
    #
    mostly_blank = [
        i
        for i, page in enumerate(reader.pages)
        if len(page.extract_text().lower()) < 100
    ]
    for i in mostly_blank:
        _store_temp_data(reader, i, kind="mostly_blank")
    good_indicies = [i for i in rng if i not in mostly_blank]
    if len(good_indicies) == 0:
        return None
    rng = sequential_ranges(good_indicies)
    return rng


def _store_temp_data(reader, page, kind, title="", author=""):
    global removed_pages_tracker
    if reader:
        try:
            meta = reader.metadata
        except Exception:
            meta = None
            pass
    else:
        meta = None
    title = meta.get("/Title") if meta else title
    author = meta.get("/Author") if meta else author
    removed_pages_tracker.append((title, author, page, kind))
    return


def detect_range_from_target_page(
    reader: p.PdfReader,
    start: int = 1,
) -> List[Tuple[int, int]]:
    """Detect the page range of the target page in a PDF file.

    Args:
        reader (p.PdfFileReader): The PDF reader object for the file.
        start (int): The page number to start searching from.
        pdf_url (str): The URL (Path) of the PDF file.

    Returns:
        rng (List[Tuple[int, int]]): A list of tuples with the start and end page numbers.
    """
    target_start = start
    end = len(reader.pages)
    for i, page in enumerate(reader.pages):
        content = text_normalize(page.extract_text())
        if any([target for target in TARGETS if target in content]):
            target_start = i
            _store_temp_data(reader, i, kind="target")
            return (target_start, end)
    return (target_start, end)


def find_part3_range(reader: p.PdfReader) -> List[Tuple[int, int]]:
    """
    Heuristic model for locating the page range of Part III in an Audit report.
    Args:
        *reader* (p.PdfReader): PyPDF2 PdfReader object for the PDF file
    Returns:
        *List[Tuple[int, int]]*: a list representing the page range of Part III
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

    # Attempt to assign part 3 start and part 4 start
    try:
        part_3_start = int(contains_piii[-1])
        # When p3 is not the first page, we need to increment by one page
        # so as not to pick up the cover page
        if part_3_start > 0:
            part_3_start += 1
    except IndexError:
        part_3_start = None
        pass
    try:
        part_4_start = int(contains_piv[-1])
    except IndexError:
        part_4_start = None
        pass

    end = len(reader.pages)

    # Edge case: part 3 starts before page 10 and pdf is longer than 50 pages
    if part_3_start is not None and part_3_start < 10 and end > 50:
        rng = detect_range_from_target_page(reader, part_3_start)
        return rng

    # Best case scenario: Have p3 and p4:
    if part_3_start is not None and part_4_start is not None:
        # if p4 comes before p3, return p3 to end
        if int(part_3_start) > int(part_4_start):
            rng = (part_3_start, end)
            return rng
        else:
            rng = (part_3_start, part_4_start)
            return rng

    # If only p3 is present, return p3 to end
    if part_3_start is not None and part_4_start is None:
        rng = (part_3_start, end)
        return rng

    # If no p3 or p4, attempt target page detection
    if part_3_start is None and part_4_start is None:
        try:
            rng = detect_range_from_target_page(reader)
            return rng
        except Exception:
            return None


def get_part3_pgs(pdf_dir):
    REMOVED_PAGES_CUZ_NO_TABLES = []
    pgs = []
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
        part3_range = find_part3_range(reader)
        if not part3_range:
            continue

        # Remove pages that have very little text content
        part3_range = remove_mostly_blank_pages_from_range(reader, part3_range)
        if not part3_range:
            continue
        # part3_range is now a list of tupled ranges (start, end)

        for rng in part3_range:
            start, end = int(rng[0]), int(rng[1])
            # Find pages containing tables
            try:
                table_pages = [
                    page
                    for page in range(start, end + 1)
                    if page_contains_table(pdf_url, page, include_stream=True)
                ]
            except IndexError:
                print(f"Error reading file {pdf_url}")
                continue
            if table_pages:
                pgs.append((pdf_url, table_pages[0], table_pages[-1]))

    # Create a dataframe of the page ranges
    df = pd.DataFrame(pgs, columns=["pdf_url", "start", "end"])
    try:
        # Save the error pages to a separate file for manual inspection
        df[df.start == "Error"].to_csv("error_pages.csv")
    except Exception:
        pass

    # Remove the error pages
    df = df[df.start != "Error"]
    df["pages"] = df.end.astype(int) - df.start.astype(int) if start != end else 1
    return df


def convert_pages_to_bitmap(
    pdf_path: str, output_dir: str, page_ranges: List[Tuple[int, int]]
) -> None:
    """
    Convert specific pages from a PDF to bitmap images.

    :param pdf_path: str, path to the input PDF file
    :param output_dir: str, path to the directory where the output images will be saved
    :param page_ranges: list of tuples, each tuple contains the start and end page numbers (inclusive) to be converted
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the PDF
    images = pdf2image.convert_from_path(pdf_path)

    # Iterate through the specified page ranges
    for start_page, end_page in page_ranges:
        for page_num in range(
            start_page, end_page + 1 if start_page == end_page else end_page
        ):
            if (
                0 <= page_num < len(images)
            ):  # Check if the page number is within the valid range
                # Save the bitmap image
                file = pdf_path.split("/")[-1]
                images[page_num].save(
                    os.path.join(output_dir, f"{file}_page_{page_num + 1}.bmp"), "BMP"
                )


def pipe_data(pdf_dir: str = "./allpdf", output_dir: str = "./images"):
    clean(pdf_dir)
    print("Finding page ranges for Part III...", end=" ")
    data = get_part3_pgs(pdf_dir)
    data.to_csv("part3_pages.csv")
    print("Done")
    print("Converting pages to images...", end=" ")
    for _, row in tqdm(data.iterrows(), total=len(data)):
        convert_pages_to_bitmap(
            row.pdf_url, output_dir, [(int(row.start), int(row.end))]
        )
    print("Done")
    print(f"All done! Now we have {len(os.listdir(output_dir))} images")


if __name__ == "__main__":
    pipe_data()
    removed_pgs = pd.DataFrame(
        removed_pages_tracker, columns=["title", "author", "pg", "reason"]
    ).to_csv("removed_pages.csv")
