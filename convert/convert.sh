#!/bin/bash
python3 clean.py zips pdf

if [ ! -d "pdf" ]; then
  mkdir pdf
fi

for f in pdf/*; do
  filename="$(basename "$f")"
  pdf_file="$(echo "$filename" | sed 's/\.[^.]*$/.pdf/')"
  if [ -f "pdf/$pdf_file" ]; then
    echo "PDF version already exists: $pdf_file"
    continue
  fi
	if [ "$(head -c 4 "$f")" = "%PDF" ]; then
		echo "PDF detected, moving to pdf directory"
		mv "$f" "pdf/$pdf_file"
		continue
	fi
	echo "Converting: $f"
	libreoffice --headless --convert-to pdf --outdir pdf "$f"
	rm "$f"
done