# MAKESHELL = \bin\sh
VENV = venv/bin
FILE = activate
ACTIVATE = . $(VENV)/$(FILE)
PIP = $(VENV)/pip
RM = rm -rf
RM_MISC = find .. -name .DS_Store -type f -delete
UNZIPPED = ../data/unzipped
PYTHON = $(VENV)/python
UNOCONV = $(VENV)/unoconv
PDF = ../data/pdf


setup:
	python3 -m venv venv
	echo $(ACTIVATE)
	$(ACTIVATE)
	$(PIP) install -r requirements.txt

clean: 
	echo $(RM)
	$(RM) $(UNZIPPED)/*
	$(RM) $(PDF)/*
	$(RM) *.pyc
	$(RM_MISC)

test: $(PYTHON) test_extract_all.py

run: sh ../phil.sh