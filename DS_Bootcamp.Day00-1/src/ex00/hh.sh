#!/bin/bash

# Check if an argument (vacancy name) is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <vacancy-name>"
    exit 1
fi

VACANCY_NAME=$1
OUTPUT_FILE="hh.json"
VALUE="20"

# Encode the vacancy name for the URL
ENCODED_VACANCY_NAME=$(echo "$VACANCY_NAME" | jq -sRr @uri)

# Make the API request to get the first 20 vacancies
curl -s "https://api.hh.ru/vacancies?text=$ENCODED_VACANCY_NAME&per_page=$VALUE" \
     -H "User-Agent: Mozilla/5.0" | jq '.' > hh.json

# Check if the request was successful
if [ $? -ne 0 ]; then
    echo "Failed to retrieve data from the API"
    exit 1
fi

echo "Vacancies data for '$VACANCY_NAME' saved in '$OUTPUT_FILE'."