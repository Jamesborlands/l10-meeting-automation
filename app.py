from flask import Flask, request, jsonify, send_file
import os
import tempfile
import shutil
from datetime import datetime
from l10_sheet_automation import L10SheetAutomation
from l10_processor import parse_l10_json
import traceback
import requests
from io import BytesIO

app = Flask(__name__)

# Configuration
EXCEL_STORAGE_URL = os.environ.get('EXCEL_STORAGE_URL', '')
WEBHOOK_RETURN_URL = os.environ.get('WEBHOOK_RETURN_URL', '')

@app.route('/health', methods=['GET'])
def health():
    """Health check for Render"""
    return jsonify({'status': 'healthy', 'service': 'L10 Automation'})

@app.route('/debug', methods=['GET'])
def debug():
    """Debug endpoint to check server state"""
    return jsonify({
        'current_dir': os.getcwd(),
        'files': os.listdir('.'),
        'xlsx_files': [f for f in os.listdir('.') if f.endswith('.xlsx')]
    })

@app.route('/echo', methods=['POST'])
def echo():
    """Echo endpoint to see exactly what Zapier sends"""
    try:
        raw_data = request.get_data(as_text=True)
        json_data = request.json
        
        return jsonify({
            'raw_data_length': len(raw_data),
            'raw_data_preview': raw_data[:500],
            'json_keys': list(json_data.keys()) if json_data else None,
            'json_structure': str(json_data)[:500] if json_data else None,
            'headers': dict(request.headers),
            'content_type': request.content_type
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process-l10', methods=['POST'])
def process_l10():
    """Main webhook endpoint for Zapier"""
    working_file = None
    excel_file = None
    
    try:
        print("Received L10 processing request")
        
        # Capture raw request data for debugging
        raw_data = request.get_data(as_text=True)
        print(f"=== RAW REQUEST DATA (first 500 chars) ===")
        print(raw_data[:500])
        
        # Get JSON from Zapier
        data = request.json
        print(f"=== PARSED REQUEST STRUCTURE ===")
        print(f"Top-level keys: {list(data.keys()) if data else 'None'}")
        
        # Try different possible data locations
        meeting_json = None
        
        # Try standard location
        if 'meeting_data' in data:
            meeting_json = data['meeting_data']
            print("Found meeting_data in standard location")
        # Try if data IS the meeting data
        elif 'NEW TO-DOS' in data or 'new_commitments' in data:
            meeting_json = data
            print("Data IS the meeting data (no wrapper)")
        # Try nested structure
        elif 'data' in data and isinstance(data['data'], dict):
            if 'meeting_data' in data['data']:
                meeting_json = data['data']['meeting_data']
                print("Found meeting_data in nested structure")
        
        if meeting_json is None:
            meeting_json = data  # Last resort - use entire payload
            print("Using entire payload as meeting data")
        
        print(f"Meeting JSON type: {type(meeting_json)}")
        print(f"Meeting JSON keys: {list(meeting_json.keys()) if isinstance(meeting_json, dict) else 'Not a dict'}")
        excel_url = data.get('excel_url', EXCEL_STORAGE_URL)
        
        # Parse the meeting data
        if isinstance(meeting_json, str):
            meeting_data = parse_l10_json(meeting_json)
        else:
            meeting_data = parse_l10_json(meeting_json)  # Always call parse_l10_json to trigger conversion
        
        print(f"Parsed meeting data with {len(meeting_data.get('NEW TO-DOS', []))} new TODOs and {len(meeting_data.get('ISSUES LIST (IDS)', []))} issues")
        
        # Download the current Excel file or use template
        if excel_url:
            print(f"Downloading Excel from: {excel_url}")
            response = requests.get(excel_url)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
                tmp.write(response.content)
                excel_file = tmp.name
        else:
            # Use local template
            excel_file = 'L10 Summary Template 1.xlsx'
            if not os.path.exists(excel_file):
                return jsonify({'error': 'No Excel file provided and no template found'}), 400
        
        # Create a working copy to preserve the original
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            shutil.copy(excel_file, tmp.name)
            working_file = tmp.name
        
        print(f"Working with Excel file: {working_file}")
        
        # Use L10SheetAutomation which adds a new sheet tab
        automation = L10SheetAutomation(working_file)
        
        # Get sheet names before
        print(f"Sheets before: {automation.wb.sheetnames}")
        
        # Process the meeting data
        result = automation.create_next_l10_sheet_from_data(
            meeting_data,
            'weekly'
        )
        
        # CRITICAL: The automation saves to self.workbook_path which is the temp file
        # But we need to make sure it's actually saved
        # Force save to ensure changes are written
        automation.wb.save(working_file)
        automation.wb.close()
        
        print(f"Sheets after save: {result}")
        print(f"File size: {os.path.getsize(working_file)} bytes")
        
        # Generate filename with the new sheet name
        output_filename = f"L10_Meeting_{result['new_sheet_name'].replace(' ', '_')}.xlsx"
        
        # Return the updated file with the new sheet tab
        return send_file(
            working_file,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"Error processing L10: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
    
    finally:
        # Cleanup temp files
        for temp_file in [excel_file, working_file]:
            if temp_file and os.path.exists(temp_file) and temp_file.startswith('/tmp'):
                try:
                    os.remove(temp_file)
                except:
                    pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)