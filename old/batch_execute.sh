#!/bin/bash
mkdir -p data/zip

directory="zips"

# First need to remove duplicated files:
# --------------------------------------
# Create an associative array to store base names
declare -a base_names

# print the number of files in the directory
echo "Number of files in directory: $(ls -1 "$directory" | wc -l)"

# Loop through each file in the directory
for file_path in "${directory}"/*; do
  # Extract the base name from the file path
  base_name="$(basename -- "$file_path" | cut -d. -f1)"
  # Check if the base name already exists in the array
  if [[ " ${base_names[*]} " == *" ${base_name} "* ]]; then
    # If the base name already exists, remove the file
    rm "$file_path"
    echo "Removed file: $file_path"
  else
    # If the base name does not exist, add it to the array
    base_names+=("$base_name")
  fi
done

# print the number of files in the directory
echo "Number of files in directory: $(ls -1 "$directory" | wc -l)"

count=0
ls zips/*.zip | xargs -n 100 > batches.txt

while read -r line; do
    IFS=' ' read -ra batch <<< "$line"
    for file in "${batch[@]}"; do
        cp "$file" data/zip
    done
    sh arm64phil.sh
    rm data/zip/*
    mv extracted extracted_batch$count
    rm -rf extracted
    count=$((count+1))
done < batches.txt

rm batches.txt
