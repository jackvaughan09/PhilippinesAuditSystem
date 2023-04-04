"""
Helper functions for extract.py

Author: @jackvaughan09 + @hudnash
"""

import pandas as pd
import PyPDF2 as p
from config import CANON_HEADERS
from fuzzywuzzy import fuzz


def good_match(og: str, ref: list[str]):
    good = ""
    approx = 0
    og = og.lower()
    for target in ref:
        new_approx = fuzz.token_sort_ratio(og, target)
        if new_approx > approx:
            approx = new_approx
            good = target
    if approx < 60:
        good = og
    return good


def find_part3_rng(pdf_url):

    reader = p.PdfReader(pdf_url)
    contains_piii = []
    contains_pv = []

    for i, pg in enumerate(reader.pages):
        content = pg.extract_text().lower()
        if "part iii" in content:
            contains_piii.append(str(i))
        if "part iv" in content:
            contains_pv.append(str(i))

    if len(contains_piii) == 0 or len(contains_pv) == 0:
        return "0"

    pg_range = "-".join([contains_piii[-1], contains_pv[-1]])
    return pg_range


def header_match_tables(dfs: list[pd.DataFrame]):
    global match
    print("Assigning canon headers to all dataframes...")
    out = []
    for i, df in enumerate(dfs):
        #####################
        # Header Detection
        # if there are headers for a particular table,
        # camelot has shoved them into the first row of the df.

        # clean and store values of first row
        first_row = df.iloc[0].apply(lambda x: x.replace("\n", ""))

        # try to match each entry in first row to a header in CANON_HEADERS
        # if it can't find a match for a particular entry, returns the original value
        match_attempt = [good_match(val, CANON_HEADERS) for val in first_row]

        # ---------------------------------------------------------------
        # inferred rule learned from research:
        # if there are less than 2 matches, then the first row is not a header row.
        # ---------------------------------------------------------------

        # check if first row values match target headers
        if len(set(CANON_HEADERS).intersection(set(match_attempt))) > 2:
            # if yes, set the global match to the match_attempt
            match = match_attempt

            # set df columns to match, filter out first row, and append to out
            df.columns = match
            df = df.iloc[1:]
            out.append(df.astype(str))
        else:
            # if no, then set the df columns to the global match
            try:
                df.columns = (
                    match  # <-- assumes that match is defined by a previous iteration
                )
                #   which is not always the case. TODO: prevent this data loss.
            except Exception as e:
                print(
                    f"The match value {match_attempt} is incongruent with\n\
                    the dataframe size."
                )
                continue
            out.append(df.astype(str))
    print("Done!")
    return out
