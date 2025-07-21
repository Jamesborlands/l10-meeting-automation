from flask import Flask, request, send_file, jsonify
import tempfile
import os
from l10_processor import populate_l10_from_text
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/populate-l10', methods=['POST'])
def populate_l10_endpoint():
    """
    Webhook endpoint for Zapier/n8n to call
    Expects JSON data in the request body
    """
    try:
        # Get JSON data from request
        json_data = request.json
        
        # Save JSON to temporary file
        temp_json = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(json_data, temp_json)
        temp_json.close()
        
        # Path to your template (store this on your server)
        template_path = "L10 Summary Template 1.xlsx"
        
        # Create temporary file for output
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        output_path = temp_output.name
        temp_output.close()
        
        # Populate the template
        populate_l10_from_text(temp_json.name, template_path, output_path)
        
        # Return the file
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=f"L10_Meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Cleanup temp files after sending
        os.unlink(temp_json.name)
        
        return response
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy", "service": "L10 Excel Population"})

if __name__ == '__main__':
    # For local testing
    app.run(debug=True, port=5000)