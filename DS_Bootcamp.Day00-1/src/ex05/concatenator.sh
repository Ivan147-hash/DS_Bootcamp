#!/bin/bash

OUTPUT_FILE="hh_result.csv"

# Checking for CSV files.
shopt -s nullglob
CSV_FILES=(*.csv)

if [[ ${#CSV_FILES[@]} -eq 0 ]]; then
       echo "Error: There are no available CSV files to merge."
       exit 1
fi

# Create an output file and add a header
echo "id, created_at, name, has_test, alternate_url" >> "$OUTPUT_FILE"

# Merge all CSV files
for file in "${CSV_FILES[@]}"; do
    tail -n +2 "$file" >> "$OUTPUT_FILE"
done

echo "Data saved to $OUTPUT_FILE."