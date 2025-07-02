#!/bin/bash

INPUT_FILE="../ex01/hh.csv"
OUTPUT_FILE="hh_sorted.csv"

# Checking for a filter
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Filter file $INPUT_FILE not found."
    exit 1
fi

# Sort the file by the 'created_at' and 'id' columns, keeping the title
{
    head -n 1 "$INPUT_FILE"
    tail -n +2 "$INPUT_FILE" | sort -t, -k2,2 -k1,1n
} > "$OUTPUT_FILE"

echo "Data saved to $OUTPUT_FILE."

