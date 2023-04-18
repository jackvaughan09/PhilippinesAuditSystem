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
]
FILTER_COLUMNS = [
    "references",
    "status of implementation",
]
AUTOCORRECT_DICT = {
    "ref": "references",
    ".Ref": "references",
    "ref.": "references",
    "refer- ence": "references",
    "Refer- ence": "references",
    "ref:": "references",
    "observations and recommendations": "audit observation",
    "Observations and Recommendations": "audit observation",
    "Ref": "references",
    "status": "status of implementation",
    "Status": "status of implementation",
    "action": "management action",
    "audit findings": "audit observation",
    "audit finding": "audit observation",
    "auditor’s rejoinder": "management action",
    "mgt. acti on": "management action",
    "r e f e r e n c e": "references",
    "audit observations/ findings/ recommendations": "audit observation",
    "status of implementation/rea son why it is not implemented": "status of implementation",
    "auditor’s validation results": "audit observation",
    "ref. cy 2012 aar (page no.)": "references",
    "status of implementation /reason why it is not implemented": "status of implementation",
    "remarks": "recommendations",
    "ref no.": "references",
    "status of implementation/reason why it is not implemented": "status of implementation",
    "status of implementation/ reason why it is not implemented": "status of implementation",
    "status of implementation/r eason why it is not implemented": "status of implementation",
    "result of validation": "status of implementation",
    "audit observation/ findings/ recommendation": "audit observation",
    "auditor’s validation and evaluation": "audit observation",
    "status of implementatio n (full, partial, ongoing or non implementat ion)": "status of implementation",
    "r emarks": "recommendations",
    "auditobservations and recommendations": "audit observation",
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
OBSERVATION_SUBSTITUTES = ["no.", ""]
REFERENCES_SUBSTITUTES = ["ref", "ref. no."]
