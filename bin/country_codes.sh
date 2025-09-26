#!/bin/bash

# Output file path (can be adjusted)
OUTPUT_FILE="src/cafi/data/country_codes.txt"

echo "Generating list of active 2-letter country codes..."

# Try to use iso-codes if installed
if [ -f "/usr/share/xml/iso-codes/iso_3166.xml" ]; then
  grep 'alpha_2_code' /usr/share/xml/iso-codes/iso_3166.xml \
    | sed -E 's/.*alpha_2_code="([A-Z]{2})".*/\1/' \
    | sort \
    | tail -n +2 \
    > "$OUTPUT_FILE"
  echo "Country codes extracted from iso-codes package."
else
  echo "iso-codes package not found. Falling back to online data source..."
  exit 1
fi
