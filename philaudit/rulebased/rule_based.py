import re
from typing import List
import math
import camelot
import fitz
from indicators import ANNEXES, PART_4_INDICATORS, TARGETS
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

# compile regex patterns once
spaces_re = re.compile(r"\s+")
linebreak_re = re.compile(r"([a-zA-Z0-9])(\n)([a-zA-Z0-9])")
camelcase_re = re.compile(r"([a-z])([A-Z])([a-z])")
punctuation_re = re.compile(r"([:,;.])(?!\s)")
roman_re = re.compile(r"(?<![a-zA-Z])i *v(?![a-zA-Z])")


def normalize_text(text: str) -> str:
    """Normalize text by removing linebreaks, camelCase, and punctuation.

    :param text: Text to normalize
    :return: Normalized text
    """
    text = linebreak_re.sub(
        r"\1 \3", text
    )  # if linebreak between two alphanumeric characters, replace with space
    text = camelcase_re.sub(r"\1 \2\3", text)  # split camelCase
    text = punctuation_re.sub(r"\1 ", text)  # add space after punctuation
    text = roman_re.sub("iv", text)  # fix roman numeral iv
    text = spaces_re.sub(" ", text)  # ensure single spaces
    text = text.replace("\n", " ")  # remove all linebreaks
    return text.lower().strip()


def sequential_ranges(lst: List[int]) -> List[range]:
    """
    Takes a list of integers and returns a list of range objects representing the sets
    of sequential integers.

    :param lst: List of integers
    :return: List of ranges
    """
    ranges = []
    start = lst[0]
    end = lst[0]
    i = 1
    while i < len(lst):
        if lst[i] - 1 != lst[i - 1]:
            end = lst[i - 1]  # Set end to the last element of the current range
            ranges.append(range(start, end + 1))
            start = lst[i]  # Update start to the new range's first element
        i += 1
    ranges.append(range(start, lst[-1] + 1))  # Append the last range
    return ranges


class PhilPage:
    # if page has fewer than this many characters (and no table), it is blank
    BLANK_THRESHOLD = 75
    # if page has more than this % of image area, it is an image and needs to be removed
    IMAGE_AREA_THRESHOLD = 0.5
    # if target indicator is found and page has fewer than this many words, it is a cover page
    COVER_PAGE_WORD_THRESHOLD = 3

    # ######################################################################## #
    # While these thresholds have served us well, they are likely not perfect. #
    # ######################################################################## #

    def __init__(self, page, path, page_num):
        self.page = page
        self.path = path
        self.page_num = page_num

        self._content = None
        self._table_status = None

        self.is_toc = False  # table of contents
        self.is_cover_page = False
        self.p4_indicator = False  # e.g. "part iv"
        self.target_indicator = False  # e.g. "status of implementation of prior years’ audit recommendations"
        self.annex_indicator = False  # e.g. "annex"
        self._setup_indicators()

        self._is_image = None
        self._is_blank = None

    def _setup_indicators(self):
        content = self.content
        if any([x in content for x in PART_4_INDICATORS]):
            self.p4_indicator = True

        if any([x in content for x in TARGETS]):
            self.target_indicator = True
            # Check if page is a cover page by checking if it contains
            # a target indicator and fewer characters than the threshold.
            if len(content.split(" ")) < self.COVER_PAGE_WORD_THRESHOLD:
                self.is_cover_page = True

        if any([x in content for x in ANNEXES]):
            self.annex_indicator = True

        if not self.is_toc and "table of contents" in content:
            self.is_toc = True

    @property
    def content(self):
        if self._content is None:
            self._content = self._clean_content()
        return self._content

    def _clean_content(self):
        return normalize_text(self.page.extract_text())

    @property
    def is_blank(self):
        if self._is_blank is None:
            self._is_blank = self._page_is_blank()
        return self._is_blank

    def _page_is_blank(self):
        if (
            len(self.content.split(" ")) < self.BLANK_THRESHOLD
            and not self.contains_table
        ):
            return True
        else:
            return False

    @property
    def contains_table(self):
        if self._table_status is None:
            self._table_status = self._page_contains_table(self.path, self.page_num)
        return self._table_status

    def _page_contains_table(self, path, page_num):
        # Extract tables
        tables = camelot.read_pdf(  # camelot is 1-indexed
            path, pages=str(page_num + 1), flavor="lattice", suppress_stdout=True
        )
        if len(tables) > 0:
            return True
        else:
            return False

    @property
    def is_image(self):
        if self._is_image is None:
            self._is_image = self._page_is_image()
        return self._is_image

    def _page_is_image(self):
        try:
            page_image = fitz.open(self.path)[self.page_num]
        except (RuntimeError, fitz.FileDataError) as e:
            raise Exception(f"Page {self.page_num} is not a valid PDF page: {str(e)}")
        image_area = 0.0
        for img_info in page_image.get_image_info():
            bbox = img_info["bbox"]
            area = abs(bbox[2] - bbox[0]) * abs(bbox[3] - bbox[1])
            image_area += area
        return (image_area / page_image.rect.size) < self.IMAGE_AREA_THRESHOLD


class PhilDocAnalyzer:
    def __init__(self, pdf_path):
        self.path = pdf_path
        try:
            self.reader = PdfReader(pdf_path)
        except PdfReadError as e:
            raise Exception(f"Error {e}. Could not read PDF file: {pdf_path}")
        self.start = 0
        self.end = len(self.reader.pages)
        self._setup()

        self._target_range = None

    def _setup(self):
        """Wrap each reader page in a PhilPage object and assign start page & end pages
        for target search.

        If a table of contents is found, the start page is the page after
        the table of contents. Otherwise, the start page is the first page
        of the document.

        The end page is the last page containing a Part IV indicator or the last page
        in the document.

        Doing this all at once is more efficient than having to loop through the pages
        multiple times.
        """
        pages = []
        contains_part4_indicator = []
        for i, page in enumerate(self.reader.pages):
            phil_page = PhilPage(page, self.path, i)
            pages.append(phil_page)
            # only assign start page if it hasn't been assigned yet
            if phil_page.is_toc and self.start == 0:
                self.start = i + 1
            # only collect part 4 indicator indexes after start page has been assigned
            if self.start != 0 and phil_page.p4_indicator:
                contains_part4_indicator.append(i)
        # only change end page if part 4 indicators were found
        if len(contains_part4_indicator) > 0:
            self.end = contains_part4_indicator[-1]
        self.pages = pages

    @property
    def target_range(self):
        if self._target_range is None:
            self._target_range = self._detect_target_range()
            self._target_range = self._remove_unwanted_pages_from_range()
        return self._target_range

    def _detect_target_range(self):
        """
        Detect the page range of Part III tables from the target page.
        Finds the first page after `start` containing a target phrase
        (see `config.TARGETS` variable).
        If a suitable target cannot be found, return original start to
        end of file.

        Args:
        - start (int): The 0-index page number to start searching from.
        - end (int): The 0-index page number to stop searching at.
        Returns:
        - rng (range): The 0-index range of PDF pages with target tables
        """
        target_start = self.start
        for i, page in enumerate(self.pages[self.start : self.end]):
            i += self.start  # adjust for start
            if page.target_indicator:
                target_start = i
                if not page.contains_table:
                    target_start += 1
                break
        return range(target_start, self.end)

    def _remove_unwanted_pages_from_range(self):
        temp_range = list(self._target_range)
        for i, page in enumerate(
            self.pages[self._target_range[0] : self._target_range[-1] + 1]
        ):
            i = i + self._target_range[0]
            if any(
                [
                    page.is_image,
                    page.annex_indicator,
                    page.is_cover_page,
                    page.is_blank,
                    not page.contains_table,
                ]
            ):
                temp_range.remove(i)
                continue
        return sequential_ranges(temp_range)

    def __attrs__(self):
        return self.__dict__.keys()
