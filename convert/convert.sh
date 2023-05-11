#!/bin/bash
create_pdf_directory() {
  if [ ! -d "pdf" ]; then
    mkdir pdf
  fi
}

unzip_and_locate_target_files() {
  echo "Unzipping and locating target files..."
  python3 clean.py zips pdf
  echo "Done!"
}

process_files() {
  total_files=$(ls pdf/* | wc -l)
  processed_files=0

  for f in pdf/*; do
    filename="$(basename "$f")"
    pdf_file="$(echo "$filename" | sed 's/\.[^.]*$/.pdf/')"
    if [ -f "pdf/$pdf_file" ]; then
      # echo "PDF version already exists: $pdf_file"
      continue
    fi
    if [ "$(head -c 4 "$f")" = "%PDF" ]; then
      # echo "PDF detected, moving to pdf directory"
      mv "$f" "pdf/$pdf_file"
      continue
    fi
    # echo "Converting: $f"
    libreoffice --headless --convert-to pdf --outdir pdf "$f"
    rm "$f"

    processed_files=$((processed_files + 1))
    echo "$processed_files" | pv -N "Converting files" -s "$total_files" -l -W -p -t -e -r > /dev/null
  done
}


cleanup() {
  # remove any files that are not pdfs
  for f in pdf/*; do
    if [ "$(head -c 4 "$f")" != "%PDF" ]; then
      rm "$f"
    fi
  done
}

main() {
  create_pdf_directory
  unzip_and_locate_target_files
  process_files
  cleanup
}

main
