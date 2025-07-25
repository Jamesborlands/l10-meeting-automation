#!/usr/bin/env python3
"""
Test script to verify the Render deployment
"""

import requests
import json
import os

# Replace this with your actual Render URL
RENDER_URL = "https://l10-meeting-automation-29fl.onrender.com"

def test_render_health():
    """Test if the Render app is running"""
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        print(f"🏥 Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_render_debug():
    """Test the debug endpoint"""
    try:
        response = requests.get(f"{RENDER_URL}/debug", timeout=10)
        print(f"🔍 Debug check: {response.status_code}")
        if response.status_code == 200:
            debug_info = response.json()
            print(f"✅ Current directory: {debug_info.get('current_dir')}")
            print(f"✅ Excel files found: {debug_info.get('xlsx_files')}")
            return True
        else:
            print(f"❌ Debug check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Debug check error: {e}")
        return False

def test_render_processing():
    """Test the main processing endpoint on Render"""
    
    # Load sample data
    with open('sample_l10_data.json', 'r') as f:
        sample_data = json.load(f)
    
    # Prepare the request payload
    payload = {
        "meeting_data": sample_data,
        "excel_url": ""  # Will use local template
    }
    
    print("🧪 Testing Render processing...")
    
    try:
        response = requests.post(
            f'{RENDER_URL}/process-l10',
            json=payload,
            timeout=60  # Render might be slower
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Save the returned Excel file
            filename = 'test_render_output.xlsx'
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Excel file saved as: {filename}")
            print(f"✅ File size: {len(response.content)} bytes")
            print("🎉 Render test PASSED!")
            return True
            
        else:
            print(f"❌ Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all Render tests"""
    print("🚀 Testing Render Deployment")
    print(f"URL: {RENDER_URL}")
    print("="*50)
    
    # Update this with your actual Render URL
    if "your-app-name" in RENDER_URL:
        print("❌ Please update RENDER_URL with your actual Render app URL")
        return
    
    health_ok = test_render_health()
    debug_ok = test_render_debug()
    
    if health_ok and debug_ok:
        processing_ok = test_render_processing()
        
        if processing_ok:
            print("\n🎉 All Render tests PASSED!")
        else:
            print("\n❌ Processing test failed")
    else:
        print("\n❌ Basic health checks failed")

if __name__ == "__main__":
    main()