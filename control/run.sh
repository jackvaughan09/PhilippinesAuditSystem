#!/usr/bin/sh
venv/bin/python3 clean.py ../data/zip ../data/pdf
sh convert.sh ../data/pdf
venv/bin/python3 mksheet.py ../data/pdf