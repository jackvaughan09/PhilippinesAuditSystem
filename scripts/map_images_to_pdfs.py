import os
import re
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def integer_ranges(lst):
    """
    Converts a list of integers into a string representing continuous ranges.

    :param lst: List of integers.
    :return: A string representing continuous ranges of integers.
    """
    if not lst:
        return ""
    lst.sort()
    start, end = lst[0], lst[0]
    result = []
    for num in lst[1:]:
        if num == end + 1:
            end = num
        else:
            result.append(f"{start}-{end}" if start != end else str(start))
            start, end = num, num
    result.append(f"{start}-{end}" if start != end else str(start))
    return ", ".join(result)


def match_validated_images_to_pdfs(df: pd.DataFrame, images_path: str) -> str:
    """
    Uses the metadata DataFrame from `create_document_metadata()` to match the validated images to the PDFs.
    Returns a DataFrame with a string of page numbers for each PDF representing the pages that will be scraped.

    :param df: A DataFrame of document metadata including paths and identifiers.
    :param images_path: Path to the directory containing the validated images.
    :return: A DataFrame with an added 'pages' column representing the pages to be scraped.
    """
    pg_list = []
    for _, row in tqdm(df.iterrows(), desc="Mapping pages to Metadata"):
        pages = [file for file in os.listdir(images_path) if row.identifier in file]
        page_numbers = [file.split("_")[-1].replace(".png", "") for file in pages]
        # Sometimes files have been downloaded twice and a page number in parentheses, e.g. "name_(1).png", appears in the name. Although duplicates
        # have already been removed, we need to remove the page number in parentheses to prevent errors casting to int.
        page_numbers = [
            int(re.sub(r"\(\d+\)", "", page_number)) for page_number in page_numbers
        ]
        page_str = integer_ranges(page_numbers)
        pg_list.append(page_str)
    df["pages"] = pg_list
    return df


def page_str_pg_count(s):
    """
    Counts the total number of pages represented in a string of page ranges.

    :param s: A string of page numbers or ranges, e.g. "1-10, 11, 13-15".
    :return: The total count of individual pages represented by the string.
    """
    if s == "":
        return 0
    ranges = s.split(", ")
    ranges = [r.split("-") for r in ranges]
    ranges = [
        range(int(r[0]), int(r[1]) + 1)
        if len(r) > 1
        else range(int(r[0]), int(r[0]) + 1)
        for r in ranges
    ]
    pages = [x for r in ranges for x in list(r)]
    return len(pages)


def main():
    root = sys.argv[1]  # Should be a year directory from within PhilAuditStorage
    year = Path(root).name
    metadata_root = os.path.join(root, "..", "Metadata")
    metadata_path = os.path.join(metadata_root, f"{year}_metadata.csv")
    image_root = os.path.join(root, "..", "Images", year, "Include")

    df = pd.read_csv(metadata_path)
    df = match_validated_images_to_pdfs(df, image_root)
    df["pg_count"] = df.pages.apply(page_str_pg_count)
    df["pageless"] = df.pg_count.apply(lambda x: x == 0)
    df.to_csv(metadata_path, index=False)
    print("Done! Metadata updated.")


main()
