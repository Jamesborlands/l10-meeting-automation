#!/usr/bin/env python3
"""
Simple test of the new L10 automation features
"""

from l10_processor import L10Processor
from datetime import datetime
import os

def test_automation():
    """Test the L10 automation with sample data"""
    processor = L10Processor()
    
    print("=== Testing L10 Automation ===")
    
    # Check for required files
    if not os.path.exists('L10 Summary Template 1.xlsx'):
        print("ERROR: L10 Summary Template 1.xlsx not found!")
        return
    
    if not os.path.exists('l10_output.txt'):
        print("ERROR: l10_output.txt not found!")
        return
    
    print("✓ Found required files")
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f'automated_l10_{timestamp}.xlsx'
    
    # Run the automation
    print("\nRunning automation...")
    result = processor.process_l10_automation(
        previous_template_path='L10 Summary Template 1.xlsx',
        new_data_path='l10_output.txt',
        output_path=output_path,
        meeting_cadence='weekly',
        last_meeting_date=datetime.now().strftime('%m/%d/%Y')
    )
    
    print("\n=== AUTOMATION COMPLETE ===")
    print(f"✓ Output saved to: {result['output_path']}")
    print(f"✓ Next meeting: {result['next_meeting_date']}")
    print(f"✓ New TO-DOs: {result['new_todos_count']}")
    print(f"✓ Updated TO-DOs: {result['updated_todos_count']}")
    print(f"✓ AI items for review: {result['ai_items_added']}")
    
    print("\nPlease check the output file to verify:")
    print("1. Sheet was duplicated correctly")
    print("2. Next meeting date was updated")
    print("3. AI Identified Items section was added at the bottom")
    print("4. No duplicate TO-DOs were added")

if __name__ == "__main__":
    test_automation()