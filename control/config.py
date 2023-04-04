#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIG.PY

Created on Sat Aug 27 17:55:03 2022

@author: hudsonnash
"""

TARGET_SENTENCE = [
    "status",
    "implementation",
    "prior",
    "audit",
    "recommendations",
]
CANON_HEADERS = [
    "audit observation",
    "recommendations",
    "references",
    "status of implementation",
    "reasons for partial/non-implementation",
    "management action",
    "observations and recommendations",
]
AUTOCORRECT_DICT = {
    "ref": "references",
    ".Ref": "references",
    "ref.": "references",
    "refer-ence": "references",
}  # TODO: regex matching when checking this, saves entries
FILENAME_TARGET = ["Status", "Audit"]
BULLET_STRS = [
    " 1. ",
    " 2. ",
    " 3. ",
    " 4. ",
    " a.",
    " b. ",
    " c. ",
    " d. ",
    " e. ",
    " f. ",
    " g. ",
]
ABBREV_CITY_NAMES = {"IGACOS": "IslandGardenCityofSamal"}
OVERFLOW_TARGET_COLS = ["audit observation", "recommendations", "references"]
