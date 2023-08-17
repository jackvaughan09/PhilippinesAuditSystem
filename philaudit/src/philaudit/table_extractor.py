import logging
import warnings

import camelot

logging.getLogger("camelot").setLevel(logging.WARNING)


class TableExtractor:
    def __init__(self, pdf_path: str, pages: str):
        self.path = pdf_path
        self.pages = pages
        self.is_image_based = False
        self.no_lattice = False
        self.table_list = None
        # Configure logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        self._setup_table_list(pdf_path, pages)

    def _setup_table_list(self, pdf_path: str, pages: str) -> None:
        """
        Set up the table list by reading the PDF with the given path and pages.

        :param pdf_path: Path to the PDF file
        :param pages: Pages to read
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                self.table_list = camelot.read_pdf(
                    pdf_path, pages=pages, flavor="lattice"
                )
            except Exception as e:
                self.table_list = None
                self.logger.error(f" {e} during PDFExtractor construction.")
                return

            if len(self.table_list) == 0:
                self.no_lattice = True
                self.logger.info(f" {pdf_path} has no lattice tables. Flagging.")
                return

            # Check if there is a UserWarning that matches the image-based warning
            for warning in w:
                if issubclass(warning.category, UserWarning) and "image-based" in str(
                    warning.message
                ):
                    self.is_image_based = True
                    self.logger.info(
                        f" {pdf_path} has image-based target pages. Flagging."
                    )
                    return

    def read_pdf(self) -> list:
        """
        Read the PDF and return the extracted tables.

        :return: List of extracted tables
        """
        if self.table_list:
            return self.table_list
        else:
            self.logger.error(f" Failed to read PDF: {self.path}")
            return []
