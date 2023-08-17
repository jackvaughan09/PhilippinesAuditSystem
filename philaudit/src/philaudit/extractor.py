import logging

import pandas as pd

from philaudit.document_table import DocumentTable
from philaudit.table_extractor import TableExtractor
from philaudit.text_normalizer import TextNormalizer


class Extractor:
    def __init__(self, pdf_path: str, pages: str):
        self.path = pdf_path
        self.pages = pages
        self.text_normalizer = TextNormalizer()
        self.table_extractor = TableExtractor(pdf_path, pages)
        self.doc_table_creator = DocumentTable(
            self.table_extractor.table_list, self.text_normalizer
        )
        self.logger = logging.getLogger(__name__)

    @property
    def doctable(self) -> pd.DataFrame:
        return self.doc_table_creator.doctable
