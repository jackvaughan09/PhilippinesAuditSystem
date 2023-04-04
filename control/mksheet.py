#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MKSHEET.PY

Created on Wed Jun 22 12:25:52 2022

@author: hudsonnash
"""

import os
import sys
from datetime import date
from extract_all import extract_all


def get_new_wb_name():
    return date.today().strftime("%B %d, %Y")


if __name__ == "__main__":
    data_url = sys.argv[1]
    df = extract_all(data_url)
    if not os.path.exists("../data/xlsx"):
        os.mkdir("../data/xlsx")
    print("Exporting data to xlsx")
    df.to_excel("../data/xlsx/" + get_new_wb_name() + ".xlsx")
    print("All done!")
