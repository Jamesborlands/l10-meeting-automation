#!/usr/bin/env python3
"""
Test script to simulate a local request to the Flask app
"""

import requests
import json
import os

def test_local_flask_app():
    """Test the Flask app running locally"""
    
    # Load sample data
    with open('sample_l10_data.json', 'r') as f:
        sample_data = json.load(f)
    
    # Prepare the request payload (same format as Zapier would send)
    payload = {
        "meeting_data": sample_data,
        "excel_url": ""  # Will use local template
    }
    
    print("🧪 Testing local Flask app...")
    print(f"Payload keys: {list(payload.keys())}")
    print(f"Meeting data has {len(sample_data.get('NEW TO-DOS', []))} TODOs")
    
    try:
        # Send request to local Flask app
        response = requests.post(
            'http://localhost:8000/process-l10',
            json=payload,
            timeout=30
        )
        
        print(f"✅ Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Save the returned Excel file
            filename = 'test_local_output.xlsx'
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Excel file saved as: {filename}")
            print(f"✅ File size: {len(response.content)} bytes")
            print("🎉 Local test PASSED!")
            
        else:
            print(f"❌ Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to local Flask app.")
        print("   Make sure you're running: python3 app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_local_flask_app()