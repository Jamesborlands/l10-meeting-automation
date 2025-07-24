#!/usr/bin/env python3
"""
L10 Meeting Automation Runner
Usage: python3 run_l10_automation.py [json_file] [excel_file]
"""

import sys
import os
import json
from datetime import datetime
from l10_processor import L10Processor, parse_l10_json

def find_latest_l10_excel():
    """Find the most recent L10 Excel file"""
    excel_files = []
    
    # Look for files with date patterns
    for f in os.listdir('.'):
        if f.endswith('.xlsx') and ('l10' in f.lower() or 'populated' in f.lower()):
            excel_files.append(f)
    
    if not excel_files:
        # Try to find template
        if os.path.exists('L10 Summary Template 1.xlsx'):
            return 'L10 Summary Template 1.xlsx'
        else:
            raise FileNotFoundError("No L10 Excel files found!")
    
    # Sort by modification time to get the most recent
    excel_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return excel_files[0]

def main():
    print("=== L10 MEETING AUTOMATION ===")
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Get input files
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        # Look for the most recent JSON file
        json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'l10' in f.lower()]
        if json_files:
            json_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            json_file = json_files[0]
        else:
            print("ERROR: No JSON file provided or found!")
            print("Usage: python3 run_l10_automation.py <json_file> [excel_file]")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        excel_file = sys.argv[2]
    else:
        excel_file = find_latest_l10_excel()
    
    print(f"JSON Input: {json_file}")
    print(f"Excel Input: {excel_file}")
    
    # Load and parse JSON
    try:
        with open(json_file, 'r') as f:
            meeting_data = parse_l10_json(f.read())
        print(f"✓ Loaded meeting data successfully")
    except Exception as e:
        print(f"ERROR loading JSON: {e}")
        sys.exit(1)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = f"L10_Meeting_{timestamp}.xlsx"
    
    # Check if output already exists
    if os.path.exists(output_file):
        # Add time to make unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"L10_Meeting_{timestamp}.xlsx"
    
    # Run automation
    try:
        processor = L10Processor()
        result = processor.process_l10_automation(
            excel_file,
            meeting_data,
            output_file,
            'weekly'  # Change to 'biweekly' if needed
        )
        
        print("\n=== RESULTS ===")
        print(f"✓ Output: {result['output_path']}")
        print(f"✓ Next meeting: {result['next_meeting_date']}")
        print(f"✓ New TO-DOs: {result['new_todos_count']}")
        print(f"✓ AI items added: {result['ai_items_added']}")
        
        # Archive the JSON file
        archive_dir = "archive"
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        
        archive_name = f"{archive_dir}/processed_{os.path.basename(json_file)}"
        os.rename(json_file, archive_name)
        print(f"\n✓ Archived JSON to: {archive_name}")
        
    except Exception as e:
        print(f"\nERROR during automation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()