"""
Helper functions for extract.py

Author: @jackvaughan09 + @hudnash
"""

import pandas as pd
import PyPDF2 as p
from config import CANON_HEADERS, TARGET_SENTENCE
from fuzzywuzzy import fuzz
from typing import List


def good_match(og: str, ref: List[str]):
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
    target_pg = []

    for i, pg in enumerate(reader.pages):
        content = pg.extract_text().lower()
        if "part iii" in content:
            contains_piii.append(str(i))
        if "part iv" in content:
            contains_pv.append(str(i))
        if [target for target in TARGET_SENTENCE if target in content] == len(
            TARGET_SENTENCE
        ):
            target_pg.append(str(i))

    # Worst case: if there is no Part III and no target page, return 0
    if len(contains_piii) == 0 and len(target_pg) == 0:
        return "0"

    # if there is no Part III, attempt target page detection
    # sometimes Part III is not labeled as such, but is still present
    if len(contains_piii) == 0 and len(target_pg) > 0:
        return target_pg[-1] + "-end"

    # if there is Part III but no Part IV, return Part III to end
    if len(contains_pv) == 0:
        pg_range = contains_piii[-1] + "-end"
        return pg_range

    # if both Part III and Part IV are present, return Part III to Part IV
    part_3_start = contains_piii[-1]
    part_4_start = contains_pv[-1]
    if int(part_3_start) > int(part_4_start):
        return contains_piii[-1] + "-end"
    elif int(part_3_start) < int(part_4_start):
        return "-".join([contains_piii[-1], contains_pv[-1]])
    else:
        return contains_piii[-1] + "-end"


def header_match_tables(dfs: List[pd.DataFrame]):
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

            # set df columns to match, filter out first row (old headers), and append to out
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
