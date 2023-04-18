import os
import pandas as pd
from extract import extract
import logging
from logging_config import setup_logging
from typing import List
from config import OBSERVATION_SUBSTITUTES, REFERENCES_SUBSTITUTES


def remove_dfs_w_nonunique_headers(dfs: List[pd.DataFrame]) -> List[pd.DataFrame]:
    # TODO: prevent this from happening in the first place or find a way to fix it.
    #      Source of the problem is how goodmatch is converting some headers to duplicates.
    #      Specifically pertaining to the similarity between status of implementation
    #      and reasons for partial/non-implementation.

    """
    Removes dataframes with non-unique headers.
    Returns a list of dataframes with unique headers.
    Logs a warning containing the filename of any dataframes
    that are removed.

    Args:
        dfs (List[pd.DataFrame]): list of dataframes to be filtered.

    Returns:
        List[pd.DataFrame]: list of dataframes with unique headers.
    """

    rule_breakers = [
        dfs[i].source.unique()[0]
        for i, df in enumerate(dfs)
        if len(df.columns) != len(set(df.columns))
    ]
    logging.warning(
        f"""The following files have non-unique headers and will be dropped: \
{rule_breakers}"""
    )
    dfs = list(filter(lambda x: len(x.columns) == len(set(x.columns)), dfs))
    return dfs


def fix_alternate_observation_colname_cases(
    dfs: List[pd.DataFrame],
) -> List[pd.DataFrame]:
    """
    Fixes dataframes with known alternate column names for audit observations.

    Args:
        dfs (List[pd.DataFrame]): list of dataframes to be fixed.

    Returns:
        List[pd.DataFrame]: list of dataframes with fixed headers.
    """

    for i, df in enumerate(dfs):
        if any([col in df.columns for col in OBSERVATION_SUBSTITUTES]):
            for col in OBSERVATION_SUBSTITUTES:
                if col in df.columns:
                    if "audit observation" in df.columns:
                        dfs[i]["audit observation"] = (
                            df[col] + " " + df["audit observation"]
                        )
                        dfs[i].drop(columns=[col], inplace=True)
                    else:
                        df.rename(columns={col: "audit observation"}, inplace=True)
    return dfs


def fix_alternate_references_colname_cases(dfs):
    """
    Fixes dataframes with known alternate column names for references.

    Args:
        dfs (List[pd.DataFrame]): list of dataframes to be fixed.

    Returns:
        List[pd.DataFrame]: list of dataframes with fixed headers.
    """

    for i, df in enumerate(dfs):
        if any([col in df.columns for col in REFERENCES_SUBSTITUTES]):
            for col in REFERENCES_SUBSTITUTES:
                if col in df.columns:
                    if "references" in df.columns:
                        dfs[i]["references"] = df[col] + " " + df["references"]
                        dfs[i].drop(columns=[col], inplace=True)
                    else:
                        df.rename(columns={col: "references"}, inplace=True)
    return dfs


def extract_all(pdf_dir) -> pd.DataFrame:
    setup_logging()
    dfs = []
    logging.info("Beginning extraction process...")
    for fi in os.listdir(pdf_dir):
        if os.path.splitext(fi)[1] == ".pdf":
            dfs.append(extract(os.path.join(pdf_dir, fi)))
    logging.info(f"Finished extracting relevant tables from {len(dfs)} files")

    logging.info("Time to do some cleaning!")
    # remove NoneType dfs (there shouldn't be any but this is safe.)
    dfs = list(filter(lambda x: x is not None, dfs))
    logging.info("Nonetype values removed.")

    # eliminating empty dfs
    dfs = list(filter(lambda x: len(x) > 0, dfs))
    logging.info("Empty dataframes removed.")

    # eliminate dfs with non-unique headers
    dfs = remove_dfs_w_nonunique_headers(dfs)

    # fixing dfs with known column name alternatives
    dfs = fix_alternate_observation_colname_cases(dfs)
    dfs = fix_alternate_references_colname_cases(dfs)
    logging.info("Dataframes with empty column names fixed.")

    # concat resulting dfs
    full_df = pd.concat(dfs, ignore_index=True)
    full_df = full_df.reset_index(drop=True)

    # ensure column order is consistent
    try:
        full_df = full_df[
            [
                "audit observation",
                "recommendations",
                "status of implementation",
                "reasons for partial/non-implementation",
                "management action",
                "references",
                "source",
            ]
        ]
    except KeyError:
        logging.warning("Column order is not consistent.")
        pass

    return full_df
