#!/bin/bash

INPUT_FILE="../ex03/hh_positions.csv"
OUTPUT_FILE="hh_uniq_positions.csv"

# Checking for a filter
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Filter file $INPUT_FILE not found."
    exit 1
fi

# Count unique name values ​​and their number
{
    echo "name, count" > "$OUTPUT_FILE"
    tail -n +2 "$INPUT_FILE" | awk -F, '{count[$3]++} END {for (name in count) print "" name "," count[name]}' | sort -t, -k2,2nr
 } >> "$OUTPUT_FILE"

echo "Data saved to $OUTPUT_FILE."