import logging
import re

import pandas as pd

ADDITIONAL_COLUMNS = [
    "corruption",
    "type",
    "notes",
    "dc_name",
    "dc_corruption",
    "dc_type",
    "dc_notes",
    "arb_name",
    "arb_corruption",
    "arb_type",
    "arb_notes",
]


class DocumentTable:
    def __init__(self, table_list: list, text_normalizer):
        self.table_list = table_list
        self._doctable = None
        self._overflow_indices = None
        self.text_normalizer = text_normalizer
        self.logger = logging.getLogger(__name__)

    def _create_doc_table(self) -> pd.DataFrame:
        """Create a table of all tables in the document."""
        if self.table_list is None:
            self.logger.error("Table list is not provided.")
            return None
        return pd.concat([table.df for table in self.table_list], ignore_index=True)

    def _data_in_headers(self, headers) -> bool:
        return any(
            [h for h in headers if len(str(h)) > 83]
        )  # NOTE: hard coded value 83 is an estimate

    def _set_headers(self) -> list:
        headers = self._doctable.iloc[0].to_list()
        if not self._data_in_headers(headers):
            to_drop = []
            for i, row in self._doctable.iterrows():
                if row.to_list() == headers:
                    to_drop.append(i)
            self._doctable = self._doctable.drop(index=to_drop)
            self._doctable = self._doctable.reset_index(drop=True)
        else:
            headers = [str(x) for x in range(len(self._doctable.columns))]
        return headers

    def _clean_doc_table(self) -> pd.DataFrame:
        """Clean the document table."""
        if self._doctable is None:
            self.logger.critical(
                f"Document table is not created! {__name__} failed to execute."
            )
            return None
        headers = self._set_headers()
        self._doctable = self._overflow_repair()
        self._doctable = self._doctable.applymap(self.text_normalizer.normalize)
        self._doctable.columns = [
            self.text_normalizer.normalize(headers) for headers in headers
        ]
        for column in ADDITIONAL_COLUMNS:
            self._doctable[column] = ""

        self._doctable = self._doctable.reset_index(drop=True)
        return self._doctable

    @property
    def doctable(self) -> pd.DataFrame:
        """Property to get the document table."""
        if self._doctable is None:
            self._doctable = self._create_doc_table()
            self._doctable = self._clean_doc_table()
        return self._doctable

    def _overflow_repair(self) -> pd.DataFrame:
        overflow_indices = self._get_overflow_indices()
        cols = self._doctable.columns.tolist()
        for i in overflow_indices:
            if i == 0:  # Skip the first row, can't be overflow
                continue
            try:
                self._doctable.loc[i - 1, cols] += " " + self._doctable.loc[i, cols]
            except:
                raise f"Error at index {i}"
        self._doctable = self._doctable.drop(index=overflow_indices)
        return self._doctable

    def _get_overflow_indices(self) -> list:
        """Get indices of overflow rows."""
        if self._overflow_indices is None:
            self._overflow_indices = self._find_regex_overflow()
        return self._overflow_indices

    def _find_regex_overflow(self) -> list:
        indicies = []
        observation_col = self._find_observation_col()  # TODO: make this more robust
        self._doctable["distinct"] = self._doctable[observation_col].apply(
            is_distinct_audit
        )
        distinct = self._doctable.distinct.sum()
        if distinct > 1 and distinct != len(self._doctable):
            indicies.extend(
                self._doctable.loc[self._doctable.distinct == False].index.tolist()
            )
        self._doctable = self._doctable.drop(columns=["distinct"])
        return indicies

    def _find_observation_col(self) -> str:
        return self._doctable.columns[0]


distinct_re = re.compile(r"(\d+\.)|(\)\s)|(\s\d+\s)|(\d+\s+)")


def is_distinct_audit(string):
    """
    Something consistent in the audit observation column is that overflow rows do
    not contain a numbered 'index' e.g. 1. or 2)  etc. in the first 10 or so
    characters in the string. This function checks for that pattern and returns True
    if it is found.

    Note: This is not a perfect solution, as some of the observations do not follow
    this pattern. However, it's pretty amazing how well it works.

    Parameters
    ----------
    string : str
        The string to check for the pattern.

    Returns
    -------
    bool : True if the pattern is found, False otherwise.
    """
    string = str(string)[:8]
    if distinct_re.findall(string):
        return True
    return False
