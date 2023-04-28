import os
import pandas as pd
import PyPDF2 as p
from PyPDF2.errors import PdfReadError
import pdf2image
import sys


FILENAME_TARGET = ["Status", "Audit"]
TARGET_SENTENCE = [
    "status",
    "audit",
    "implementation",
    "recommendations",
    "prior",
    "year",
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


def clean(directory):
    """Remove duplicate files and common unwanted files from a directory.
    Args:
        directory (str): The directory to clean.
    """
    print(len(os.listdir(directory)))
    seen = set()
    for filename in os.listdir(directory):
        if filename not in seen:
            seen.add(filename)
        else:  # duplicate file
            print("duplicate file: " + filename)
            os.remove(directory + filename)
            continue
        bad_names = [".docx", ".doc", "Part-1", "Certificate", "Part1", "Independent"]
        if any(bad_name in filename for bad_name in bad_names):
            os.remove(directory + filename)
    print(len(os.listdir(directory)))


def find_part3_pgs(pdf_url: str):
    """
    Finds the page range of Part III of a PDF.
    Args:
        *pdf_url* (str): path to the PDF file
    Returns:
        *str*: a string representing the page range of Part III
             If no Part III is found, returns "0"

    ### Description:
    - Worst case: if there is no Part III and no target page, return "0"
    - if there is no Part III, attempt target page detection
    - if there is Part III but no Part IV, return Part III to end
    - if both Part III and Part IV are present, return Part III to Part IV
    """
    try:
        reader = p.PdfReader(pdf_url)
    except PdfReadError as e:
        print(f"Error reading file {pdf_url}: {e}")
        return (pdf_url, "Error", "Error")
    contains_piii = []
    contains_piv = []
    target_pg = []

    for i, pg in enumerate(reader.pages):
        content = pg.extract_text().lower()
        if "part iii" in content:
            contains_piii.append(i)
        if "part iv" in content:
            contains_piv.append(i)
        if all([target for target in TARGET_SENTENCE if target in content]):
            target_pg.append(i)

    # Worst case: if there is no Part III and no target page, return 0
    if len(contains_piii) == 0 and len(target_pg) == 0:
        return "0"

    # if there is no Part III, attempt target page detection
    # sometimes Part III is not labeled as such, but is still present
    # relying on the target sentence capture to find the page
    # has some problems, but is better than nothing
    if len(contains_piii) == 0 and len(target_pg) > 0:
        # if there is a target page, return first target page to end
        return (pdf_url, target_pg[0], len(reader.pages))

    # if there is Part III but no Part IV, return Part III to end
    if len(contains_piv) == 0:
        return (pdf_url, contains_piii[0], len(reader.pages))

    # if both Part III and Part IV are present, return Part III to Part IV
    part_3_start = contains_piii[-1]
    part_4_start = contains_piv[-1]
    if int(part_3_start) > int(part_4_start):
        return (pdf_url, contains_piii[0], len(reader.pages))
    elif int(part_3_start) < int(part_4_start):
        return (pdf_url, contains_piii[-1], contains_piv[-1])
    else:
        return (pdf_url, contains_piii[0], len(reader.pages))


def get_part3_pgs(pdf_dir):
    lens = []
    for file in os.listdir(pdf_dir):
        if file.endswith(".pdf"):
            pdf_url = os.path.join(pdf_dir, file)
            lens.append((find_part3_pgs(pdf_url)))

    # Create a dataframe of the page ranges
    df = pd.DataFrame(lens, columns=["pdf_url", "start", "end"])
    df = df[df.start != "Error"]
    df["pages"] = df.end.astype(int) - df.start.astype(int)
    return df


def convert_pages_to_jpeg(pdf_path, output_dir, page_ranges):
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
            start_page - 1, end_page
        ):  # start_page - 1 because Python uses zero-based indexing
            if (
                0 <= page_num < len(images)
            ):  # Check if the page number is within the valid range
                # Save the bitmap image
                file = pdf_path.split("/")[-1]
                images[page_num].save(
                    os.path.join(output_dir, f"{file}_page_{page_num + 1}.jpeg"), "JPEG"
                )


if __name__ == "__main__":
    pdf_dir = sys.argv[0]
    output_dir = sys.argv[1]
    clean(pdf_dir)
    data = get_part3_pgs(pdf_dir)
    for i, row in data.iterrows():
        convert_pages_to_jpeg(row.pdf_url, output_dir, [(int(row.start), int(row.end))])
    print("All done!")
