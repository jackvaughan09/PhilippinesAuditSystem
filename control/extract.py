"""
Author: @jackvaughan09
"""

import camelot
import pandas as pd
from config import CANON_HEADERS
from extracttools import header_match_tables, find_part3_rng
from philformat import overflow_repair, phil_format


def extract(pdf_url):
    pg_rng = find_part3_rng(pdf_url)
    if len(pg_rng) == 0:
        print("No Part III found. Continuing.")
        return pd.DataFrame(columns=CANON_HEADERS)

    print(f"Attempting to read tables from: {pdf_url}" "\nThis might take a while.")
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
        print("No tables found. Continuing.")
        return pd.DataFrame(columns=CANON_HEADERS)
    print(f"Finished reading {len(dfs)} tables from file {pdf_url}")
    dfs = header_match_tables(dfs)
    dfs = phil_format(dfs, pdf_url)
    try:
        out = pd.concat(dfs).reset_index(drop=True)
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame(columns=CANON_HEADERS)
    # one more for good measure.
    # out = overflow_repair(out)
    return out
