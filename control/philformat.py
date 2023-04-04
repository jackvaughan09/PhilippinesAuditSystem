"""
This is our main data manipulation module
slayer of overflow, maker of pretty dataframes.
The functions here are run after all dataframes 
have been collected from a file in order
to standardize the output for analysis later on.

Author: @jackvaughan09
"""

import pandas as pd
from config import AUTOCORRECT_DICT, CANON_HEADERS


def polish(df, ref=CANON_HEADERS):
    try:
        df = df.fillna("")
        df = df.applymap(lambda x: str(x).replace("\n", " "))
        df = df.applymap(space_lambda)
    except Exception:
        print("Error occurred, returning empty df.\nData might have been lost.")
        return pd.DataFrame(columns=ref)
    return df


# NOTE: this is a hacky solution to the problem of standardizing column names
# across all dataframes. Could definitely be improved.
def standardize_columns(df):
    for k, v in AUTOCORRECT_DICT.items():
        if k in df.columns:
            df = df.rename(columns={k: v})
    # find difference between df and canon headers
    diff = set(CANON_HEADERS) - set(df.columns)
    if diff:
        # create the canon column and fill with blank strings
        for label in diff:
            df[label] = ""
    return df


def overflow_repair(df):
    droplist = []
    df = df.fillna("").reset_index(drop=True)
    for i, row in df.iterrows():
        if i == 0:
            continue
        if sum([len(x.strip()) == 0 for x in row]) < 2:
            originating_row = df.loc[i - 1]
            overflow = df.loc[i]
            for j, y in enumerate(originating_row):
                comb = str(y) + " " + str(overflow[j])
                originating_row[j] = comb
            df.loc[i - 1] = originating_row
            droplist.append(i)

    if droplist == []:
        return df
    for i in droplist:
        df = df.drop(index=i)
    df = df.reset_index(drop=True)
    print(f"Fixed {len(droplist)} overflow rows.")
    return df


def space_lambda(x):
    words = [w.strip() for w in x.split()]
    return " ".join(words)


def status_lambda(x):

    x = (
        str(x)
        .replace("P ", "")
        .replace("N ", "")
        .replace("I ", "")
        .replace(" ot ", "Not ")
        .replace(" mplemented", "Implemented ")
        .replace(" artially ", "Partially ")
    )

    return x


def fix_status_columns(df):
    status_cols = [
        "status of implementation",
        "reasons for partial/non-implementation",
    ]
    for col in status_cols:
        df[col] = df[col].apply(status_lambda)
    return df


def phil_format(dfs, pdf_url):
    print("Applying formatting tools to data...")
    dfs = [polish(df) for df in dfs]
    dfs = [standardize_columns(df) for df in dfs]
    dfs = [overflow_repair(df) for df in dfs]
    dfs = [fix_status_columns(df) for df in dfs]
    # dfs = [df.applymap(space_lambda) for df in dfs]
    for df in dfs:
        df["source"] = pdf_url.split("/")[-1]
    return dfs
