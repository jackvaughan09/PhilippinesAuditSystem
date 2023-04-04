import os
import pandas as pd
from extract import extract


def extract_all(pdf_dir) -> pd.DataFrame:
    dfs = []
    print("Beginning extraction process...")
    for fi in os.listdir(pdf_dir):
        if os.path.splitext(fi)[1] == ".pdf":
            dfs.append(extract(os.path.join(pdf_dir, fi)))
    print("Finished extracting relevant tables from all files")

    print("Time to do some cleaning!")
    # remove NoneType dfs (there shouldn't be any but this is safe.)
    dfs = list(filter(lambda x: x is not None, dfs))
    print("Nonetype values removed.")
    # concat result
    full_df = pd.concat(dfs)
    return full_df
