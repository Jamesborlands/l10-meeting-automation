#!/usr/bin/env python3
"""
Test the conversion endpoint to see if Render has the latest conversion code
"""

import requests
import json

test_data = {
    "new_commitments": [
        {
            "who": "Test User",
            "task": "Test task for debugging",
            "due_date": "Next week",
            "context": "Testing conversion",
            "dependencies": "None"
        }
    ],
    "issues_discussed": [
        {
            "issue": "Test issue for debugging",
            "raised_by": "Test User",
            "context": "Testing issue conversion",
            "decision": "Test decision",
            "owner": "Test User"
        }
    ]
}

def test_conversion_endpoint():
    """Test the conversion endpoint"""
    print("🧪 Testing conversion endpoint on Render")
    print("="*50)
    
    payload = {"meeting_data": test_data}
    
    try:
        response = requests.post(
            'https://l10-meeting-automation-29fl.onrender.com/test-conversion',
            json=payload,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Conversion test results:")
            for key, value in result.items():
                print(f"  {key}: {value}")
            
            if result.get('conversion_successful'):
                print("🎉 Conversion is working on Render!")
            else:
                print("❌ Conversion is not working on Render")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Wait a bit for deployment
    import time
    print("Waiting 90 seconds for Render deployment...")
    time.sleep(90)
    
    test_conversion_endpoint()