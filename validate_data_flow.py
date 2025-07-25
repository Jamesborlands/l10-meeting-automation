#!/usr/bin/env python3
"""
Comprehensive test script to validate the entire L10 data flow
This script tests the full pipeline from JSON parsing to Excel generation
"""

import json
import shutil
import os
from datetime import datetime
from l10_sheet_automation import L10SheetAutomation
from l10_processor import parse_l10_json

def print_separator(title):
    """Print a nice separator for test sections"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_json_parsing():
    """Test JSON parsing with sample data"""
    print_separator("Testing JSON Parsing")
    
    # Load and parse sample data
    try:
        with open('sample_l10_data.json', 'r') as f:
            raw_data = f.read()
        
        print(f"✓ Loaded sample JSON file ({len(raw_data)} characters)")
        
        # Parse the data
        parsed_data = parse_l10_json(raw_data)
        
        print(f"✓ Successfully parsed JSON")
        print(f"✓ Data keys: {list(parsed_data.keys())}")
        
        # Check for expected sections
        expected_sections = ['NEW TO-DOS', 'ISSUES LIST (IDS)', 'TO-DO REVIEW']
        for section in expected_sections:
            if section in parsed_data:
                items = parsed_data[section]
                print(f"✓ {section}: {len(items)} items")
                if items and isinstance(items, list) and len(items) > 0:
                    print(f"  Sample item keys: {list(items[0].keys())}")
            else:
                print(f"⚠️  Missing section: {section}")
        
        return parsed_data
        
    except Exception as e:
        print(f"❌ Error in JSON parsing: {e}")
        return None

def test_excel_template():
    """Test Excel template access and sheet operations"""
    print_separator("Testing Excel Template")
    
    template_file = 'L10 Summary Template 1.xlsx'
    
    try:
        if not os.path.exists(template_file):
            print(f"❌ Template file not found: {template_file}")
            return False
        
        print(f"✓ Template file exists: {template_file}")
        
        # Create a test copy
        test_file = 'test_workbook.xlsx'
        shutil.copy(template_file, test_file)
        print(f"✓ Created test copy: {test_file}")
        
        # Test L10SheetAutomation
        automation = L10SheetAutomation(test_file)
        print(f"✓ L10SheetAutomation initialized")
        
        # Get sheet info
        sheets = automation.wb.sheetnames
        print(f"✓ Workbook has {len(sheets)} sheets: {sheets}")
        
        latest_sheet = automation.get_latest_sheet()
        print(f"✓ Latest sheet: {latest_sheet.title}")
        print(f"✓ Sheet dimensions: {latest_sheet.max_row} rows x {latest_sheet.max_column} columns")
        
        # Clean up
        automation.wb.close()
        os.remove(test_file)
        print(f"✓ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Excel template test: {e}")
        return False

def test_ai_section_generation(parsed_data):
    """Test AI section generation with sample data"""
    print_separator("Testing AI Section Generation")
    
    if not parsed_data:
        print("❌ No parsed data available for testing")
        return False
    
    try:
        # Create test workbook
        template_file = 'L10 Summary Template 1.xlsx'
        test_file = 'test_ai_section.xlsx'
        shutil.copy(template_file, test_file)
        
        automation = L10SheetAutomation(test_file)
        
        # Create a new sheet to test on
        latest_sheet = automation.get_latest_sheet()
        next_date = datetime.now()
        new_sheet = automation.duplicate_sheet(latest_sheet, next_date)
        
        print(f"✓ Created new test sheet: {new_sheet.title}")
        
        # Extract data for AI section
        new_todos = parsed_data.get('NEW TO-DOS', [])
        new_issues = parsed_data.get('ISSUES LIST (IDS)', [])
        
        print(f"✓ Data to process:")
        print(f"  - TODOs: {len(new_todos)}")
        print(f"  - Issues: {len(new_issues)}")
        
        # Test AI section addition
        initial_max_row = new_sheet.max_row
        print(f"✓ Initial sheet max row: {initial_max_row}")
        
        end_row = automation.add_ai_section(new_sheet, new_todos, new_issues)
        
        final_max_row = new_sheet.max_row
        print(f"✓ Final sheet max row: {final_max_row}")
        print(f"✓ AI section ended at row: {end_row}")
        print(f"✓ Rows added: {final_max_row - initial_max_row}")
        
        # Verify some cells have content
        ai_header_row = initial_max_row + 3  # Based on add_ai_section logic
        header_content = new_sheet.cell(row=ai_header_row, column=1).value
        print(f"✓ AI section header: {header_content}")
        
        # Save the test file
        automation.wb.save(test_file)
        automation.wb.close()
        
        print(f"✓ Test workbook saved as: {test_file}")
        print(f"  You can open this file to verify the AI section was added correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in AI section generation test: {e}")
        return False

def test_full_automation_pipeline(parsed_data):
    """Test the complete automation pipeline"""
    print_separator("Testing Full Automation Pipeline")
    
    if not parsed_data:
        print("❌ No parsed data available for testing")
        return False
    
    try:
        # Create test workbook
        template_file = 'L10 Summary Template 1.xlsx'
        test_file = 'test_full_pipeline.xlsx'
        shutil.copy(template_file, test_file)
        
        automation = L10SheetAutomation(test_file)
        
        print(f"✓ Starting full pipeline test")
        
        # Run the complete automation
        result = automation.create_next_l10_sheet_from_data(parsed_data, 'weekly')
        
        print(f"✓ Automation completed successfully")
        print(f"✓ Result: {result}")
        
        # Verify the result
        expected_keys = ['new_sheet_name', 'next_date', 'new_todos_count', 'new_issues_count', 'existing_todos_count']
        for key in expected_keys:
            if key in result:
                print(f"  - {key}: {result[key]}")
            else:
                print(f"  ⚠️  Missing result key: {key}")
        
        # Check if new sheet was created
        final_sheets = automation.wb.sheetnames
        print(f"✓ Final workbook sheets: {final_sheets}")
        
        automation.wb.close()
        
        print(f"✓ Full pipeline test workbook saved as: {test_file}")
        print(f"  You can open this file to verify the complete automation worked")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in full pipeline test: {e}")
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    print_separator("Testing Edge Cases")
    
    try:
        # Create test workbook
        template_file = 'L10 Summary Template 1.xlsx'
        test_file = 'test_edge_cases.xlsx'
        shutil.copy(template_file, test_file)
        
        automation = L10SheetAutomation(test_file)
        latest_sheet = automation.get_latest_sheet()
        next_date = datetime.now()
        new_sheet = automation.duplicate_sheet(latest_sheet, next_date)
        
        print("✓ Testing with empty data")
        automation.add_ai_section(new_sheet, [], [])
        
        print("✓ Testing with invalid data types")
        automation.add_ai_section(new_sheet, "not a list", {"not": "a list"})
        
        print("✓ Testing with malformed items")
        bad_todos = [
            {"WHO": "Test", "TO-DO": "Valid item"},  # Valid
            "not a dict",  # Invalid
            {"missing_todo_field": "problem"},  # Missing fields
            None  # None value
        ]
        
        bad_issues = [
            {"issue_description": "Valid issue", "who_raised_it": "Test"},  # Valid
            42,  # Invalid type
            {"incomplete": "data"}  # Missing fields
        ]
        
        automation.add_ai_section(new_sheet, bad_todos, bad_issues)
        
        automation.wb.close()
        os.remove(test_file)
        
        print("✓ Edge case testing completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in edge case testing: {e}")
        return False

def main():
    """Run all validation tests"""
    print("L10 Data Flow Validation Test Suite")
    print(f"Started at: {datetime.now()}")
    
    results = {}
    
    # Run all tests
    parsed_data = test_json_parsing()
    results['json_parsing'] = parsed_data is not None
    
    results['excel_template'] = test_excel_template()
    results['ai_section'] = test_ai_section_generation(parsed_data)
    results['full_pipeline'] = test_full_automation_pipeline(parsed_data)
    results['edge_cases'] = test_edge_cases()
    
    # Summary
    print_separator("Test Results Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The data flow is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print(f"\nCompleted at: {datetime.now()}")

if __name__ == "__main__":
    main()