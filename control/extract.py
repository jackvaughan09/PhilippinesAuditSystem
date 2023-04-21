"""
Author: @jackvaughan09
"""

import camelot
import pandas as pd
from config import CANON_HEADERS
from extracttools import extract_cleanup, find_part3_rng
import logging
from logging_config import setup_logging


def extract(pdf_url):
    setup_logging()
    missing = pd.DataFrame(
        data=[f"Missing data at {pdf_url}"].extend([None] * (len(CANON_HEADERS) - 1)),
        columns=CANON_HEADERS,
    )

    pg_rng = find_part3_rng(pdf_url)
    if len(pg_rng) == 0:
        logging.info(f"No Part III found in {pdf_url}. Continuing.")
        return missing

    # TODO: alternate method for extracting tables with Layout Parser
    # TODO: add option to use stream method if no tables detected
    logging.info(f"Attempting to read tables from: {pdf_url}")
    dfs = [
        df.df.astype(str)
        for df in camelot.read_pdf(
            filepath=pdf_url,
            flavor="lattice",
            multiple_tables=True,
            # copy_text=["v"],
            line_scale=30,
            pages=pg_rng,
        )
    ]
    if len(dfs) < 1:
        logging.info("No tables found. Continuing.")
        return missing

    logging.info(f"Finished reading {len(dfs)} tables from file {pdf_url}")
    df = extract_cleanup(dfs)
    df["source"] = pdf_url.split("/")[-1]
    df = df.reset_index(drop=True)
    return df
