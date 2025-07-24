from flask import Flask, request, jsonify, send_file
import os
import tempfile
import shutil
from datetime import datetime
from l10_processor import L10Processor, parse_l10_json
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

@app.route('/process-l10', methods=['POST'])
def process_l10():
    """Main webhook endpoint for Zapier"""
    try:
        print("Received L10 processing request")
        
        # Get JSON from Zapier
        data = request.json
        meeting_json = data.get('meeting_data', {})
        excel_url = data.get('excel_url', EXCEL_STORAGE_URL)
        return_method = data.get('return_method', 'file')
        
        # Parse the meeting data
        if isinstance(meeting_json, str):
            meeting_data = parse_l10_json(meeting_json)
        else:
            meeting_data = meeting_json
        
        print(f"Parsed meeting data with {len(meeting_data.get('NEW TO-DOS', []))} new TODOs")
        
        # Download the current Excel file
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
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"L10_Meeting_{timestamp}.xlsx"
        
        # Process the automation
        processor = L10Processor()
        result = processor.process_l10_automation(
            excel_file,
            meeting_data,
            output_file,
            'weekly'
        )
        
        print(f"Automation complete: {result}")
        
        # Return file directly to Zapier
        return send_file(
            output_file,
            as_attachment=True,
            download_name=output_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"Error processing L10: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)