from l10_processor import L10Processor, parse_l10_json
import json
import os

# Load your JSON data
print("Loading JSON data...")
with open('sample_l10_data.json', 'r') as f:
    meeting_data = parse_l10_json(f.read())

print(f"✓ Loaded meeting data with {len(meeting_data.get('HEADLINES', []))} headlines")
print(f"✓ Found {len(meeting_data.get('TO-DO REVIEW', []))} TO-DO reviews")
print(f"✓ Found {len(meeting_data.get('NEW TO-DOS', []))} new TO-DOs")

# Find your most recent populated Excel file
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and 'populated' in f]
if excel_files:
    excel_files.sort()
    latest_file = excel_files[-1]
    print(f"\nUsing Excel file: {latest_file}")
else:
    # Use template if no populated file exists
    latest_file = 'L10 Summary Template 1.xlsx'
    print(f"\nUsing template: {latest_file}")

# Run the automation
processor = L10Processor()
result = processor.process_l10_automation(
    latest_file,           # Your existing Excel file
    meeting_data,          # The parsed JSON data
    'automated_l10_output.xlsx',  # Output file
    'weekly'              # Meeting cadence
)

print("\n=== AUTOMATION COMPLETE ===")
print(f"✓ Output saved to: {result['output_path']}")
print(f"✓ Next meeting date: {result['next_meeting_date']}")
print(f"✓ New TO-DOs added: {result['new_todos_count']}")
print(f"✓ Updated TO-DOs: {result['updated_todos_count']}")
print(f"✓ Total AI items: {result['ai_items_added']}")
print(f"\nOpen '{result['output_path']}' to review the results!")