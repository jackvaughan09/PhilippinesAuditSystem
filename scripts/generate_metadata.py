import os
import sys
from pathlib import Path

import pandas as pd


def extract_path_parts(dirpath, year):
    """
    Extracts specific parts of the directory path related to the year, city/municipality, region, and barangay.

    :param dirpath: The directory path containing files.
    :param year: The year to be looked for within the path.
    :return: A tuple containing the year, city/municipality, region, and barangay, or placeholders if not found.
    """
    path_parts = dirpath.parts
    yr_idx = path_parts.index(year)
    parts = path_parts[yr_idx:]
    if len(parts) == 4:  # hard-coded to match the directory structure
        return parts
    elif len(parts) == 3:  # same as above
        return parts + ("N/A",)
    else:
        print(f"Unexpected path parts: {path_parts} for File in Path: {dirpath}")
        return ("N/A",) * 4


def create_document_metadata(root: str):
    """
    Creates a DataFrame containing metadata for documents within a specific year's audit reports.

    :param root: Absolute path to the root directory of a single year's audit reports.
    :return: DataFrame containing document metadata.
    """
    data = []
    year = Path(root).name
    for dirpath, _, filenames in os.walk(root):
        dirpath = Path(dirpath)
        for filename in filenames:
            if filename.endswith((".zip", ".pdf")):
                year, city_municipality, region, barangay = extract_path_parts(
                    dirpath, year
                )
                path = dirpath / filename
                data.append([filename, year, city_municipality, region, barangay, path])

    cols = ["document", "year", "city_or_municipality", "region", "barangay", "path"]
    df = pd.DataFrame(data, columns=cols)
    df = create_identifiers(df)
    return df


def create_identifiers(df):
    """
    Creates unique identifiers for documents based on their metadata.

    :param df: DataFrame containing document metadata.
    :return: DataFrame with added 'identifier' column.
    """
    ids = []
    for i, row in df.iterrows():
        y_tag = ""
        if not row["year"] in row["document"]:
            y_tag = row["year"] + "-"

        barangay = ""
        if row.barangay != "N/A":
            barangay = row.barangay + "_"
        ids.append(f"{row.region}_{barangay}{y_tag}{row.document[:-4]}")
    df["identifier"] = ids
    return df


def main():
    """
    Main function to execute the program. Reads path to /PAS/Year/, creates metadata, and
    saves the metadata to a CSV file in the /PAS/Metadata/ directory.
    """
    root = sys.argv[1]  # Should be a year directory from within PhilAuditStorage
    year = Path(root).name
    metadata_path = os.path.join(root, "..", "Metadata")
    df = create_document_metadata(root)
    df.to_csv(os.path.join(metadata_path, f"{year}_metadata.csv"), index=False)


if __name__ == "__main__":
    main()
