#!/bin/bash
# Weekly L10 Processing Script

echo "=== WEEKLY L10 PROCESSING ==="
echo "Date: $(date)"

# Set your directories
L10_DIR="/path/to/L10 Excel Population"
TRANSCRIPT_DIR="$L10_DIR/transcripts"
OUTPUT_DIR="$L10_DIR/outputs"

# Create directories if they don't exist
mkdir -p "$TRANSCRIPT_DIR"
mkdir -p "$OUTPUT_DIR"

# Find the latest JSON file
LATEST_JSON=$(ls -t "$TRANSCRIPT_DIR"/*.json 2>/dev/null | head -1)

if [ -z "$LATEST_JSON" ]; then
    echo "ERROR: No JSON file found in $TRANSCRIPT_DIR"
    exit 1
fi

echo "Processing: $LATEST_JSON"

# Run the automation
cd "$L10_DIR"
python3 run_l10_automation.py "$LATEST_JSON"

# Move output to outputs directory
mv L10_Meeting_*.xlsx "$OUTPUT_DIR/" 2>/dev/null

echo "Complete! Check $OUTPUT_DIR for the new file."