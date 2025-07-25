# L10 Meeting Automation System

A Flask-based web service that processes meeting transcripts and automatically updates Excel workbooks with AI-identified items.

## 🏗️ Architecture

### Core Components

1. **`app.py`** - Flask web service with REST endpoints
2. **`l10_processor.py`** - JSON/text parsing and format conversion  
3. **`l10_sheet_automation.py`** - Excel workbook manipulation
4. **`L10 Summary Template 1.xlsx`** - Excel template with meeting structure

### Key Features

- **Multi-format Support**: Handles both L10 format and alternative JSON structures
- **Automatic Sheet Creation**: Creates new dated sheet tabs for each meeting
- **AI Section Generation**: Adds "AI IDENTIFIED ITEMS" section with extracted TODOs and issues
- **Duplicate Detection**: Prevents duplicate TODOs from being added
- **Error Handling**: Robust validation and error recovery

## 📡 API Endpoints

### `POST /process-l10`
Main webhook endpoint for processing meeting data.

**Request Format:**
```json
{
  "meeting_data": {
    "NEW TO-DOS": [...],
    "ISSUES LIST (IDS)": [...],
    "TO-DO REVIEW": [...],
    "HEADLINES": [...]
  },
  "excel_url": "optional_url_to_existing_workbook"
}
```

**Response:** Excel file with new sheet and AI section populated

### `GET /health`
Health check endpoint

### `GET /debug`
Debug information about server state

## 🔄 Data Flow

1. **Input**: Meeting data via POST request (Zapier webhook)
2. **Parse**: Convert JSON to L10 format if needed (`l10_processor.py`)
3. **Process**: Create new sheet and extract TODOs/issues (`l10_sheet_automation.py`)
4. **Output**: Return updated Excel workbook

## 📊 Supported Data Formats

### L10 Format (Primary)
```json
{
  "NEW TO-DOS": [
    {
      "WHO": "Person Name",
      "TO-DO": "Task description",
      "DUE DATE": "Due date",
      "CONTEXT": "Why this task exists",
      "DEPENDENCIES": "Prerequisites"
    }
  ],
  "ISSUES LIST (IDS)": [
    {
      "issue_description": "Problem description",
      "who_raised_it": "Person who raised it",
      "root_cause": "Root cause analysis",
      "related_discussions": "Discussion points",
      "notes": "Additional notes"
    }
  ]
}
```

### Alternative Format (Auto-converted)
```json
{
  "new_commitments": [...],  // → NEW TO-DOS
  "issues_discussed": [...], // → ISSUES LIST (IDS)
  "todo_review": [...]       // → TO-DO REVIEW
}
```

## 🚀 Deployment

### Render Deployment
- **URL**: `https://l10-meeting-automation-29fl.onrender.com`
- **Auto-deploy**: Triggered by GitHub pushes to main branch
- **Environment**: Python 3.x with required dependencies

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

## 🧪 Testing

### Validation Suite
```bash
python validate_data_flow.py
```
Runs comprehensive tests of the entire pipeline.

### Manual Testing
```bash
# Test local Flask app
python test_local_request.py

# Test Render deployment  
python test_render_deployment.py
```

## 📁 File Structure

```
├── app.py                    # Flask web service
├── l10_processor.py          # Data parsing and conversion
├── l10_sheet_automation.py   # Excel manipulation
├── L10 Summary Template 1.xlsx # Excel template
├── requirements.txt          # Python dependencies
├── validate_data_flow.py     # Test suite
├── sample_l10_data.json      # Sample data for testing
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables
- `PORT`: Server port (default: 5000)
- `EXCEL_STORAGE_URL`: Optional URL for Excel file storage
- `WEBHOOK_RETURN_URL`: Optional webhook return URL

### Dependencies
- Flask: Web framework
- openpyxl: Excel file manipulation
- requests: HTTP client for external Excel files

## 🎯 Usage with Zapier

1. **Set up Zapier webhook** pointing to `/process-l10` endpoint
2. **Configure JSON payload** with meeting data in supported format
3. **Receive processed Excel file** with new sheet and AI section

### Example Zapier Payload
```json
{
  "meeting_data": {
    "NEW TO-DOS": [
      {
        "WHO": "John Doe",
        "TO-DO": "Complete quarterly report",
        "DUE DATE": "Next Friday",
        "CONTEXT": "Required for board meeting",
        "DEPENDENCIES": "Need data from finance team"
      }
    ],
    "ISSUES LIST (IDS)": [
      {
        "issue_description": "Server performance issues",
        "who_raised_it": "Jane Smith",
        "root_cause": "Increased traffic load",
        "related_discussions": "Need to upgrade infrastructure",
        "notes": "Assigned to DevOps team"
      }
    ]
  }
}
```

## 🛠️ Maintenance

The system is designed to be self-contained and requires minimal maintenance. Key considerations:

- **Template Updates**: Update `L10 Summary Template 1.xlsx` as needed
- **Format Changes**: Modify conversion logic in `l10_processor.py` 
- **Excel Logic**: Update sheet manipulation in `l10_sheet_automation.py`
- **Monitoring**: Check Render logs for any processing errors