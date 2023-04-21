"""
Helper functions for extract.py

Author: @jackvaughan09 + @hudnash
"""

import pandas as pd
import PyPDF2 as p
from config import CANON_HEADERS, TARGET_SENTENCE, AUTOCORRECT_DICT, FILTER_COLUMNS
from fuzzywuzzy import fuzz
from typing import List
import logging
from logging_config import setup_logging

setup_logging()


def good_match(og: str, ref: List[str]):
    """Tries to find an approximate match for the string [og]
    in the list [ref]. If no match is found, returns the original string.
    Args:
        og (str): string to be matched
        ref (List[str]): list of strings to match against
    Returns:
        str: the best match found in [ref] or [og] if no match is found
    """
    good = ""
    approx = 0
    og = og.lower()
    for target in ref:
        new_approx = fuzz.token_sort_ratio(og, target)
        if new_approx > approx:
            approx = new_approx
            good = target
    if approx < 60:  # tuning parameter
        good = og
    return good


def find_part3_rng(pdf_url: str):
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
        if all([target for target in TARGET_SENTENCE if target in content]):
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


def autocorrect(cols):
    for i, x in enumerate(cols):
        if x in AUTOCORRECT_DICT.keys():
            cols[i] = AUTOCORRECT_DICT[x]
    return cols


def find_match_and_first_row_header_matches(
    dfs: List[pd.DataFrame],
) -> tuple:
    """Iterates through a list of dataframes and returns the first header
    row that contains a match for at least 3 of the canonical headers.

    Args:
        dfs (List[pd.DataFrame]): list of dataframes to search

    Returns:
        match -> List[str]: list of strings representing the first row that contains
        a match for at least 3 of the canonical headers. If no match is found, returns None.

        match_inds -> List[int]: list of indices of the dataframes that contain
        a match for at least 3 of the canonical headers in the first row.

    Notes:
        Inferred rule learned from my (@jackvaughan09) research:
        If there are less than 2 matches, then the first row is not a header row.
        This is a tuning parameter. It may need to be adjusted.
    """
    p = 2  # tuning parameter for intersect with CANON_HEADERS
    match = None
    match_inds = []
    for i in range(0, len(dfs)):
        first_row = dfs[i].iloc[0].apply(lambda x: x.replace("\n", "").lower())
        first_row = autocorrect(first_row)
        match_attempt = [good_match(val, CANON_HEADERS) for val in first_row]
        if len(set(CANON_HEADERS).intersection(set(match_attempt))) > p:
            match_inds.append(i)
            if match == None:
                match = match_attempt
                # match = fix_outlier_headers(match)
    return match, match_inds


def filter_redundant_header_rows(dfs, inds):
    for i in inds:
        dfs[i] = dfs[i].iloc[1:]
    return dfs


# set all headers to the same thing -> works inplace
def standardize_columns(
    dfs: List[pd.DataFrame], match: List[str]
) -> List[pd.DataFrame]:
    droplist = []
    for i in range(0, len(dfs)):
        try:
            dfs[i].columns = match
        except Exception as e:
            logging.info(
                f"""The match value is incongruent with \
the dataframe columns {dfs[i].columns}. \
Dataframe {i} will be dropped."""
            )
            droplist.append(i)
            continue
    for i in droplist[::-1]:
        dfs.pop(i)
    return dfs


def enforce_filter_column_presence(df: pd.DataFrame):
    for col in FILTER_COLUMNS:
        if col not in df.columns:
            df[col] = "N/A"
    return df


# concatinate and check for overflow
def overflow_repair(df: pd.DataFrame):
    df = enforce_filter_column_presence(df)
    ovfl_ind = df.loc[
        (df.references == "") | (df["status of implementation"] == "")
    ].index
    logging.info(f"{len(ovfl_ind)} overflow rows detected.")
    for i in ovfl_ind:
        if i == 0:
            continue
        df.loc[i - 1, :] = df.loc[i - 1, :] + " " + df.loc[i, :]
    df.drop(index=ovfl_ind, inplace=True)
    logging.info(f"Repaired")
    return df


def space_lambda(x):
    words = [w.strip() for w in x.split()]
    return " ".join(words)


def polish(df, ref=CANON_HEADERS):
    try:
        df = df.fillna("")
        df = df.applymap(lambda x: str(x).replace("\n", " "))
        df = df.applymap(lambda x: str(x).replace("₱ ", ""))
        df = df.applymap(space_lambda)
    except Exception:
        logging.info("Error occurred, returning empty df.\nData might have been lost.")
        return pd.DataFrame(columns=ref)
    return df


def match_analysis(match):
    """_summary_

    Args:
        match (_type_): _description_

    Returns:
        _type_: _description_
    """

    return


def extract_cleanup(dfs: List[pd.DataFrame]):
    setup_logging()
    logging.info("Cleaning up dataframes...")
    dfs = [polish(df) for df in dfs]

    logging.info("Locating proper header rows...")
    match, match_inds = find_match_and_first_row_header_matches(dfs)
    if match is None:
        logging.info("No match found. Returning empty dataframe.")
        return pd.DataFrame(columns=CANON_HEADERS)

    logging.info(f"Filtering out {len(match_inds)} redundant header rows...")
    dfs = filter_redundant_header_rows(dfs, match_inds)

    logging.info("Assigning canon headers to all dataframes...")
    dfs = standardize_columns(dfs, match)

    logging.info("Concatinating dataframes...")
    df = pd.concat(dfs, ignore_index=True)
    logging.info("Checking for overflow...")
    df = overflow_repair(df)
    # df = crunch(df)
    df = df.reset_index(drop=True)
    logging.info("Done!")
    return df
