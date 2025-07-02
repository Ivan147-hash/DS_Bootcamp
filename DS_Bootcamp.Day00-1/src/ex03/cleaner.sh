#!/bin/bash

INPUT_FILE="../ex02/hh_sorted.csv"
OUTPUT_FILE="hh_positions.csv"

# Create or clear the hh_positions.csv file
echo '"id","created_at","name","has_test","alternate_url"' > hh_positions.csv

# Define an array with position levels
positions=("Junior" "Middle" "Senior")

shopt -s nocasematch

# Reading input from standard input
tail -n +2 "$INPUT_FILE" | while IFS= read -r line; do
    # Extracting fields
    id=$(echo "$line" | cut -d',' -f1)
    created_at=$(echo "$line" | cut -d',' -f2)
    name=$(echo "$line" | cut -d',' -f3)
    has_test=$(echo "$line" | cut -d',' -f4)
    alternate_url=$(echo "$line" | cut -d',' -f5)

    found_positions=()

    # Initialize a variable to store the found positions
    for position in "${positions[@]}"; do
        if [[ $name == *"$position"* ]]; then
            found_positions+=("$position")
        fi
    done

    # Generating a string to be written to CSV
    if [ ${#found_positions[@]} -gt 0 ]; then
        # Combine the found positions using "/"
        result=$(IFS=/; echo "${found_positions[*]}")
    else
        result="-"
    fi

    # Write the result to a CSV file
    echo "$id, $created_at, \"$result\", $has_test, $alternate_url" >> "$OUTPUT_FILE"
done


echo "Data saved to $OUTPUT_FILE."