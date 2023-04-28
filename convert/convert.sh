#!/bin/bash
create_pdf_directory() {
  if [ ! -d "pdf" ]; then
    mkdir pdf
  fi
}

clean_directory() {
  python3 clean.py zips pdf
}

process_files() {
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
}

main() {
  create_pdf_directory
  clean_directory
  process_files
}

main
