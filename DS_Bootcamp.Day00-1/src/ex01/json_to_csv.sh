#!/bin/bash

INPUT_FILE="../ex00/hh.json"
OUTPUT_FILE="hh.csv"
FILTER_FILE="filter.jq"

# Checking for a filter
if [[ ! -f "$FILTER_FILE" ]]; then
    echo "Error: Filter file $FILTER_FILE not found."
    exit 1
fi

# Use jq to filter the JSON and convert to CSV
{
    echo "id, created_at, name, has_test, alternate_url"
    jq -r -f "$FILTER_FILE" "$INPUT_FILE"
} > "$OUTPUT_FILE"

echo "Data saved to $OUTPUT_FILE."