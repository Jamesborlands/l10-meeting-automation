#!/usr/bin/env python3
"""
Test the new JSON format to see what happens
"""

import json
from l10_processor import parse_l10_json

# Your new test data
new_format_data = {
  "meeting_date": "2023-10-05",
  "attendees": [
    "Josh Keshen",
    "Lyndsey Dunnavant", 
    "Josh Weinberg",
    "Regan Gentry",
    "Lisa Schick"
  ],
  "headlines": [
    {
      "text": "Removal of training suggestion to archive the training policy and updates on new state audits."
    }
  ],
  "todo_review": [
    {
      "who": "Lyndsey Dunnavant",
      "todo": "Redline the training policy to include ongoing training references.",
      "status": "Not Done",
      "notes": "Lyndsey believes it is essential to retain a training policy to avoid regulatory issues.",
      "original_due": "Next meeting"
    }
  ],
  "issues_discussed": [
    {
      "issue": "The need to adjust the training policy.",
      "raised_by": "Lyndsey Dunnavant",
      "context": "The existing training policy is not being adhered to, and regulators may question training compliance.",
      "discussion_points": [
        "Lyndsey noted the current policy mentions comprehensive training that is not being provided.",
        "Josh expressed concern about removing training references completely.",
        "Josh suggested revising the training policy to include ongoing training versus a fixed schedule."
      ],
      "decision": "Lyndsey will redline the training policy for revision.",
      "owner": "Lyndsey Dunnavant"
    },
    {
      "issue": "Upcoming reports and responsibilities for state audits.",
      "raised_by": "Josh Weinberg",
      "context": "Kansas is leveraging Washington's audits, and Mississippi's audits are pending.",
      "discussion_points": [
        "Josh provided updates on audits in different states.",
        "Lyndsey mentioned Mississippi processing and possible split of work."
      ],
      "decision": "Keep monitoring the situation with state audits; further updates are needed.",
      "owner": "Josh Weinberg"
    }
  ],
  "new_commitments": [
    {
      "who": "Lyndsey Dunnavant",
      "task": "Ensure training policy is revised and prepared for compliance review.",
      "due_date": "Next meeting",
      "context": "To align with regulatory standards.",
      "dependencies": "Gather input from team and maintain policy visibility."
    },
    {
      "who": "Josh Weinberg",
      "task": "Monitor updates on audits and ensure compliance documentation is complete.",
      "due_date": "Next meeting",
      "context": "To facilitate smooth audits in future and ensure all states are compliant.",
      "dependencies": "Collaboration with state teams."
    }
  ]
}

def compare_formats():
    """Compare the two data formats"""
    print("🔍 ANALYZING NEW DATA FORMAT")
    print("="*60)
    
    # Show what keys are in the new format
    print("Keys in your new format:")
    for key in new_format_data.keys():
        print(f"  - {key}")
    
    print("\nExpected L10 format keys:")
    expected_keys = ['NEW TO-DOS', 'ISSUES LIST (IDS)', 'TO-DO REVIEW', 'HEADLINES']
    for key in expected_keys:
        print(f"  - {key}")
    
    print("\n" + "="*60)
    
    # Parse with the L10 processor
    parsed_data = parse_l10_json(new_format_data)
    
    print("After parsing with L10 processor:")
    print(f"Keys found: {list(parsed_data.keys())}")
    print(f"NEW TO-DOS count: {len(parsed_data.get('NEW TO-DOS', []))}")
    print(f"ISSUES LIST count: {len(parsed_data.get('ISSUES LIST (IDS)', []))}")
    
    if parsed_data.get('NEW TO-DOS'):
        print("NEW TO-DOS content:")
        for item in parsed_data['NEW TO-DOS']:
            print(f"  {item}")
    else:
        print("❌ No NEW TO-DOS found!")
    
    if parsed_data.get('ISSUES LIST (IDS)'):
        print("ISSUES LIST content:")
        for item in parsed_data['ISSUES LIST (IDS)']:
            print(f"  {item}")
    else:
        print("❌ No ISSUES LIST found!")

if __name__ == "__main__":
    compare_formats()