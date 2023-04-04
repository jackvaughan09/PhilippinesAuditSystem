"""
Author: @hudnash
#~! venv/bin/python
"""


#import extract
from extracttools import get_pg_rng
fi = '../extracted/pdf/01-IGACOS2010_Audit_Report.pdf'
print(get_pg_rng(fi))