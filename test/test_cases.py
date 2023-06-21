import re


def extract_basename(file_name: str) -> str:
    # Pattern to match the basename
    pattern = r"(\d*-)?([a-zA-Z]+[\d]+)"
    # Search for the pattern in the file name
    match = re.search(pattern, file_name)
    # If a match is found, return the second group (i.e., the basename)
    if match:
        return match.group(2)
    else:
        raise ValueError(f"Invalid file name format: {file_name}")


test_cases = {
    # ================================================================================
    # Long document formats
    # --------------------------------------------------------------------------------
    # --- Tested and passed                 Reason for test
    "alcoy2013": [range(30, 40)],  # no cover page long document form
    "alegria2013": [range(36, 42)],  # exclude cover page long document form
    "batan2013": [range(44, 46)],  # exclude cover page + last page
    "dagohoy2013": [range(70, 80)],  # ToC target pg detect
    "banayoyo2013": [range(37, 42)],  # exclude cover page + blank page
    "licuanbaay2011": [  # very broken ranges (blank pages)
        range(45, 48),
        range(49, 52),
        range(53, 55),
        range(56, 61),
    ],
    "penarrubia2012": [range(41, 46)],
    "sabangan2016": [range(48, 52)],
    "tadian2016": [range(47, 53)],
    "tuba2019": [range(62, 79)],  # whole doc
    "buguias2019": [range(60, 76)],
    "kabugao2019": [range(73, 94)],  # annex page
    "sablan2019": [range(71, 92)],
    "kibungan2019": [range(117, 143)],
    "latrinidad2019": [range(74, 94)],
    "bakun2019": [range(48, 66)],  # whole doc
    "bokod2019": [range(64, 81)],  # whole doc
    "itogon2019": [range(80, 106)],
    "kapangan2019": [range(60, 74)],
    "bangued2012": [range(56, 67)],  # Annex
    "bangued2016": [range(92, 105)],
    "besao2013": [range(23, 27)],
    "pilar2011": [range(35, 45)],  # annex and lots of extras
    "bangued2020": [range(85, 91)],  # picked up annex
    "lagangilang2015": [range(107, 119)],  # picked up annex
    "pilar2020": [range(81, 88)],  # annex page
    "daguioman2012": [range(58, 73)],
    "danglas2011": [range(51, 54), range(55, 56), range(57, 61)],
    "langiden2011": [range(43, 47), range(48, 49)],
    "paracelis2016": [range(56, 61)],  # only one page??
    "atok2019": [range(76, 93)],
    "pidigan2011": [range(47, 55)],  # only page 57...?
    "kabayan2019": [range(91, 115)],  # only one page
    "dolores2020": [range(121, 139)],  # whole doc
    "natonin2013": [range(26, 29)],
    "dolores2021": [range(110, 121)],
    "luna2019": [range(58, 75)],
    "dolores2018": [range(129, 147)],  # converted whole doc!
    "aguinaldo2019": [range(51, 59)],  # need to detect annex page as end of part3
    "bangued2011": [range(71, 82)],  # need to detect annex page as end of part3
    "calanasan2019": [range(47, 56)],
    # ================================================================================
    # Short/Individual document formats
    # --- Tested and passed
    "pantabangan2013": [range(0, 16)],  # exclude final blank page
    "acastaneda2013": [range(1, 6)],  # exclude first page
    "besao2016": [range(0, 6)],  # only one page
    "bontoc2016": [range(0, 12)],  # isolated doc with p iii in references column
    "luna2021": [range(0, 19)],  # start page cut off?
    "alfonso2013": [range(0, 6)],  # standard isolated document form
    "mariaaurora2013": [range(0, 8)],
    "sagada2016": [range(0, 9)],  # getting 7 as start
    #
    # --- Currently Testing --> problem identified: part iii in references column
    # ================================================================================
    # Stream document formats
    # -- Tested and passed
    "newlucena2013": [range(1, 7)],  # no columns or row demarkation (stream test)
    # -- Currently testing
    # ================================================================================
}
