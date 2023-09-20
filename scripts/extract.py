import os
import shutil
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from philaudit.extractor import Extractor


def handle_existing_file(md_acc, path):
    if os.path.exists(path):
        md_acc.append((False, None, path))
        return True
    return False


def handle_pageless(md_acc, row, pageless_dir):
    if row.pageless:
        pageless_path = os.path.join(pageless_dir, row.document)
        if handle_existing_file(md_acc, pageless_path):
            return True

        md_acc.append((True, None))
        shutil.copy(row.path, pageless_dir)
        return True
    return False


def handle_errors(md_acc, row, extractor, no_lattice_dir, image_pdfs_dir):
    if extractor.table_extractor.no_lattice:
        nl_path = os.path.join(no_lattice_dir, row.document)
        if handle_existing_file(md_acc, nl_path):
            return True
        md_acc.append((True, "Document has no lattice tables.", nl_path))
        shutil.copy(row.path, no_lattice_dir)
        return True

    if extractor.table_extractor.is_image_based:
        ipdf_path = os.path.join(image_pdfs_dir, row.document)
        if handle_existing_file(md_acc, ipdf_path):
            return True
        md_acc.append((True, "Document is image based. Missing some pages", ipdf_path))
        shutil.copy(row.path, image_pdfs_dir)
        return True

    return False


def extract_data(df, out):
    pageless_dir = os.path.join(out, "Errors", "Pageless")
    no_lattice_dir = os.path.join(out, "Errors", "No_lattice")
    image_pdfs_dir = os.path.join(out, "Errors", "Image_pdfs")
    complete_dir = os.path.join(out, "Complete")

    # initialize metadata accumulator to later append to df
    md_acc = []  # (error, error_msg, extracted_path)
    for _, row in tqdm(
        df.iterrows(),
        desc="Extracting data",
    ):
        complete_path = os.path.join(complete_dir, f"{row.identifier[:-4]}.csv")
        if handle_existing_file(md_acc, complete_path):
            continue

        if handle_pageless(md_acc, row, pageless_dir):
            continue

        extractor = Extractor(row.path, row.pages)

        if handle_errors(md_acc, row, extractor, no_lattice_dir, image_pdfs_dir):
            continue

        try:
            extractor.doctable.to_csv(complete_path, index=False)
        except Exception as e:
            md_acc.append((True, e, None))
            print(f"Error with {row.document}, skipping. Lost {row.pg_count} pages.")
            continue

        md_acc.append((False, None, complete_path))

    df["error"] = [d[0] for d in md_acc]
    df["error_msg"] = [d[1] for d in md_acc]
    df["extracted_path"] = [d[2] for d in md_acc]
    return df


def main():
    root = sys.argv[1]  # Should be a year directory from within PhilAuditStorage
    year = Path(root).name  # PhilAuditStorage/Year --> Year
    metadata_path = Path(root).parent.absolute() / "Metadata"
    metadata_file = metadata_path / f"{year}_metadata.csv"

    df = pd.read_csv(metadata_file)
    out = os.path.join(root, "..", "Extracted", year)

    # result of extract is an updated metadata file
    md = extract_data(df, out)
    print("Done! Data extracted.")
    md.to_csv(os.path.join(metadata_path, f"{year}_metadata.csv"))
    print("Metadata has been updated with errors and extracted paths.")


if __name__ == "__main__":
    main()
