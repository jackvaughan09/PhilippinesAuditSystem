#!/usr/bin/sh
for f in "$1"/*; do
  filename="$(basename "$f")"
  pdf_file="$(echo "$filename" | sed 's/\.[^.]*$/.pdf/')"
  if [ -f "../data/pdf/$pdf_file" ]; then
    echo "PDF version already exists: $pdf_file"
    continue
  fi
	if [ "$(head -c 4 "$f")" = "%PDF" ]; then
		echo "PDF detected, moving to pdf directory"
		mv "$f" "../data/pdf/$pdf_file"
		continue
	fi
	echo "Converting: $f"
	libreoffice --headless --convert-to pdf --outdir ../data/pdf "$f"
done