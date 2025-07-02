#!/bin/bash

INPUT_FILE="../ex03/hh_positions.csv"

# Checking for a filter
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Filter file $INPUT_FILE not found."
    exit 1
fi

tail -n +2 "$INPUT_FILE" | while IFS=',' read -r id created_at name has_test alternate_url; do
data=$(echo "$created_at" | cut -d'T' -f1)

if [[ ! -f "$data.csv" ]]; then
    echo '"id", "created_at", "name", "has_test", "alternate_url"' > "$data.csv"
fi
echo "$id, $created_at, $name, $has_test, $alternate_url" >> "$data.csv"
done

echo "Data saved."