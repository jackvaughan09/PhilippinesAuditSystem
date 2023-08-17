import os
import sys
from pathlib import Path

import pandas as pd
from pdf2image import convert_from_path
from tqdm import tqdm


def convert_pdf_to_images(pdf_path: str, identifier: str, output_folder: str):
    """
    Converts a PDF to PNG images, saving each page as a separate image in the specified output folder.

    :param pdf_path: The path to the PDF file to be converted.
    :param identifier: An identifier used to name the output image files.
    :param output_folder: PhilAuditStorage/Images/year/All
    """
    images = convert_from_path(pdf_path, fmt="png")
    for idx, img in enumerate(images):
        img_path = os.path.join(
            output_folder,
            f"{identifier}_page_{idx + 1}.png",  # +1 since camelot is 1-indexed
        )

        if not os.path.exists(img_path):
            img.save(img_path, "png")


def generate_page_images(df: pd.DataFrame, image_root: str):
    """
    Iterates through a DataFrame of PDF files, converting each PDF to images using the convert_pdf_to_images function.

    :param df: A DataFrame containing the paths and identifiers of the PDFs to be converted.
    :param image_root: The directory where the images will be saved.
    """

    for _, row in tqdm(df.iterrows(), desc="Converting PDFs to images"):
        path = row.path
        identifier = row.identifier
        convert_pdf_to_images(path, identifier, image_root)


def main():
    """
    Main function that reads command line arguments for input file and output directory
    and calls the generate_page_images function to convert PDFs to images.
    """

    root = sys.argv[1]  # Should be a year directory from within PhilAuditStorage
    year = Path(root).name
    metadata_root = os.path.join(root, "..", "Metadata")
    metadata_path = os.path.join(metadata_root, f"{year}_metadata.csv")
    metadata_file = pd.read_csv(metadata_path)
    image_root = os.path.join(root, "..", "Images", year, "All")
    generate_page_images(df=metadata_file, image_root=image_root)
    print("Done!")


if __name__ == "__main__":
    main()
