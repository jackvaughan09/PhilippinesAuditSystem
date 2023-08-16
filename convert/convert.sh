#!/bin/bash
unzip_and_locate_target_files() {
  echo "Unzipping and locating target files..."
  python3 clean.py /app/data
  echo "Done!"
}

process_files2() {
  find /app/data -type f \( -name "*.doc" -o -name "*.docx" \) -print0 | while IFS= read -r -d '' f; do
    echo "Processing: $f"
  done
}


process_files() {
  total_files=$(find /app/data -type f \( -name "*.doc" -o -name "*.docx" \) | wc -l)
  processed_files=0

  find /app/data -type f \( -name "*.doc" -o -name "*.docx" \) -print0 | while IFS= read -r -d '' f; do
    filename="$(basename "$f")"
    pdf_file="$(echo "$filename" | sed 's/\.[^.]*$/.pdf/')"
    pdf_path="$(dirname "$f")/$pdf_file"
    if [ -f "$pdf_path" ]; then
      # Remove the existing PDF if you want to convert again
      rm "$pdf_path"
    fi

    # Converting
    libreoffice --headless --convert-to pdf --outdir "$(dirname "$f")" "$f"
    rm "$f"

    processed_files=$((processed_files + 1))
    echo "$processed_files" | pv -N "Converting files" -s "$total_files" -l -W -p -t -e -r > /dev/null
  done
}


main() {
  unzip_and_locate_target_files
  process_files
}

main
