import re


class TextNormalizer:
    def __init__(self):
        # Regex patterns for text normalization
        self.linebreak_re = re.compile(r"([a-zA-Z0-9])(\n)([a-zA-Z0-9])")
        self.camelcase_re = re.compile(r"([a-z])([A-Z])([a-z])")
        self.punctuation_re = re.compile(r"([:,;.])(?!\s)")
        self.spaces_re = re.compile(r"\s+")

    def normalize(self, text: str) -> str:
        """
        Normalize the given text by removing linebreaks, camelCase, punctuation, and NaNs.

        :param text: Text to normalize
        :return: Normalized text
        """
        if isinstance(text, float):
            return ""
        if not isinstance(text, str):
            return text
        text = self.linebreak_re.sub(
            r"\1 \3", text
        )  # if linebreak between two alphanumeric characters, replace with space
        text = self.camelcase_re.sub(r"\1 \2\3", text)  # split camelCase
        text = self.punctuation_re.sub(r"\1 ", text)  # add space after punctuation
        text = self.spaces_re.sub(" ", text)  # ensure single spaces
        text = text.replace("\n", " ")  # remove all linebreaks
        return text.lower().strip()
