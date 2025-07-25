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
    import datetime
    return jsonify({'status': 'healthy', 'service': 'L10 Automation', 'version': '2.1', 'timestamp': datetime.datetime.now().isoformat()})

@app.route('/debug', methods=['GET'])
def debug():
    """Debug endpoint to check server state"""
    return jsonify({
        'current_dir': os.getcwd(),
        'files': os.listdir('.'),
        'xlsx_files': [f for f in os.listdir('.') if f.endswith('.xlsx')]
    })

@app.route('/test-conversion', methods=['POST'])
def test_conversion():
    """Test the data conversion function"""
    try:
        data = request.json
        meeting_json = data.get('meeting_data', {})
        
        # Import and test conversion
        from l10_processor import parse_l10_json
        
        parsed_data = parse_l10_json(meeting_json)
        
        return jsonify({
            'original_keys': list(meeting_json.keys()) if isinstance(meeting_json, dict) else 'not_dict',
            'converted_keys': list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'not_dict',
            'new_todos_count': len(parsed_data.get('NEW TO-DOS', [])),
            'issues_count': len(parsed_data.get('ISSUES LIST (IDS)', [])),
            'conversion_successful': 'NEW TO-DOS' in parsed_data or 'ISSUES LIST (IDS)' in parsed_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/process-l10', methods=['POST'])
def process_l10():
    """Main webhook endpoint for Zapier"""
    working_file = None
    excel_file = None
    
    try:
        print("Received L10 processing request")
        
        # Get JSON from Zapier
        data = request.json
        meeting_json = data.get('meeting_data', {})
        excel_url = data.get('excel_url', EXCEL_STORAGE_URL)
        
        # Parse the meeting data
        print(f"=== DEBUG: Raw meeting_json type: {type(meeting_json)} ===")
        print(f"=== DEBUG: Raw meeting_json keys: {list(meeting_json.keys()) if isinstance(meeting_json, dict) else 'Not a dict'} ===")
        
        if isinstance(meeting_json, str):
            meeting_data = parse_l10_json(meeting_json)
        else:
            meeting_data = parse_l10_json(meeting_json)  # Always call parse_l10_json to trigger conversion
        
        print(f"=== DEBUG: After parse_l10_json, keys: {list(meeting_data.keys()) if isinstance(meeting_data, dict) else 'Not a dict'} ===")
        
        print(f"=== DEBUG: Parsed meeting data ===")
        print(f"Meeting data keys: {list(meeting_data.keys())}")
        print(f"NEW TO-DOS count: {len(meeting_data.get('NEW TO-DOS', []))}")
        print(f"ISSUES LIST count: {len(meeting_data.get('ISSUES LIST (IDS)', []))}")
        
        # Debug the actual data
        if meeting_data.get('NEW TO-DOS'):
            print("NEW TO-DOS sample:")
            for i, todo in enumerate(meeting_data.get('NEW TO-DOS', [])[:2]):  # First 2 items
                print(f"  {i+1}. {todo}")
        
        if meeting_data.get('ISSUES LIST (IDS)'):
            print("ISSUES LIST sample:")
            for i, issue in enumerate(meeting_data.get('ISSUES LIST (IDS)', [])[:2]):  # First 2 items
                print(f"  {i+1}. {issue}")
        
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