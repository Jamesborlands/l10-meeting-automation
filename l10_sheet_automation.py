import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime, timedelta
import re
from copy import copy

class L10SheetAutomation:
    """
    Automates L10 meeting workflow by duplicating sheets within the same workbook
    """
    
    def __init__(self, workbook_path):
        self.workbook_path = workbook_path
        self.wb = openpyxl.load_workbook(workbook_path)
        
    def get_latest_sheet(self):
        """Find the most recent L10 sheet in the workbook"""
        # Sheets are usually named with dates, find the most recent
        sheets = self.wb.sheetnames
        print(f"Found {len(sheets)} sheets: {sheets}")
        
        # Assume the last sheet is the most recent (or we can parse dates)
        latest_sheet = self.wb[sheets[-1]]
        return latest_sheet
    
    def duplicate_sheet(self, source_sheet, new_date):
        """Duplicate a sheet and update the date"""
        # Create new sheet name (e.g., "Jul 23 2025" or match your format)
        new_sheet_name = new_date.strftime("%b %d %Y")
        
        # Copy the sheet
        new_sheet = self.wb.copy_worksheet(source_sheet)
        new_sheet.title = new_sheet_name
        
        print(f"Created new sheet: {new_sheet_name}")
        
        # Update date in the new sheet (look for date patterns)
        for row in range(1, 5):  # Check first 5 rows
            for col in range(1, new_sheet.max_column + 1):
                cell = new_sheet.cell(row=row, column=col)
                if cell.value and isinstance(cell.value, str):
                    # Look for date patterns and update them
                    if re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', str(cell.value)):
                        # Update to new date
                        cell.value = new_date.strftime("%m/%d/%Y")
                        print(f"Updated date in cell {row},{col}")
                        break
        
        return new_sheet
    
    def find_existing_todos(self, sheet):
        """Extract existing TO-DOs from the sheet"""
        existing_todos = []
        
        # Find TO-DO section
        todo_row = None
        for row in range(1, min(30, sheet.max_row)):
            for col in range(1, min(7, sheet.max_column + 1)):
                cell_value = sheet.cell(row=row, column=col).value
                if cell_value and 'TO-DO' in str(cell_value).upper():
                    todo_row = row
                    break
            if todo_row:
                break
        
        if todo_row:
            # Look for TO-DO items after the header
            for row in range(todo_row + 1, sheet.max_row + 1):
                who = sheet.cell(row=row, column=1).value
                todo = sheet.cell(row=row, column=2).value
                done = sheet.cell(row=row, column=3).value
                
                if who and todo:
                    existing_todos.append({
                        'WHO': str(who).strip(),
                        'TO-DO': str(todo).strip(),
                        'DONE?': str(done).strip() if done else '',
                        'row': row
                    })
                elif not who and not todo and row > todo_row + 5:
                    break
        
        return existing_todos
    
    def add_ai_section(self, sheet, new_todos, new_issues):
        """Add AI identified items section at the bottom of the sheet"""
        # Find the last row with content
        last_row = sheet.max_row
        
        # Add some space
        start_row = last_row + 3
        
        # Add header
        sheet.cell(row=start_row, column=1, value="AI IDENTIFIED ITEMS (Review & Move to Appropriate Sections)")
        sheet.cell(row=start_row, column=1).font = Font(bold=True, color="0066CC", size=12)
        
        current_row = start_row + 2
        
        # Add new TO-DOs
        if new_todos:
            sheet.cell(row=current_row, column=1, value="Potential New TO-DOs:")
            sheet.cell(row=current_row, column=1).font = Font(bold=True, italic=True)
            current_row += 1
            
            for todo in new_todos:
                sheet.cell(row=current_row, column=1, value=todo.get('WHO', 'TBD'))
                sheet.cell(row=current_row, column=2, value=todo.get('TO-DO', ''))
                sheet.cell(row=current_row, column=3, value='No')  # Default to not done
                sheet.cell(row=current_row, column=4, value=todo.get('NOTES', ''))
                current_row += 1
        
        # Add space before issues
        current_row += 1
        
        # Add new Issues
        if new_issues:
            sheet.cell(row=current_row, column=1, value="Potential New Issues:")
            sheet.cell(row=current_row, column=1).font = Font(bold=True, italic=True)
            current_row += 1
            
            for issue in new_issues:
                issue_text = f"{issue.get('issue', '')} (Raised by: {issue.get('raised_by', 'TBD')})"
                sheet.cell(row=current_row, column=2, value=issue_text)
                current_row += 1
        
        print(f"Added AI section starting at row {start_row}")
        return current_row
    
    def clear_completed_todos_from_new_sheet(self, sheet, todo_start_row):
        """
        Optional: Clear TO-DOs marked as 'Yes' from the new sheet
        (Based on your meeting discussion, you might NOT want this)
        """
        # This is commented out based on the meeting notes
        # You want to keep completed items for tracking
        pass
    
    def process_meeting_output(self, meeting_text):
        """Parse the meeting output text"""
        from l10_processor import parse_l10_text
        return parse_l10_text(meeting_text)
    
    def create_next_l10_sheet(self, meeting_output_file, meeting_cadence='weekly'):
        """
        Main automation function:
        1. Duplicate the latest sheet
        2. Update the date
        3. Keep existing TO-DOs (including completed ones)
        4. Add AI identified items section
        5. Save the workbook
        """
        print("=== L10 SHEET AUTOMATION ===")
        
        # Get the latest sheet
        latest_sheet = self.get_latest_sheet()
        print(f"Using sheet: {latest_sheet.title}")
        
        # Calculate next meeting date
        # Try to parse date from sheet name or find it in the sheet
        today = datetime.now()
        if meeting_cadence == 'weekly':
            next_date = today + timedelta(days=7)
        else:
            next_date = today + timedelta(days=14)
        
        # Duplicate the sheet
        new_sheet = self.duplicate_sheet(latest_sheet, next_date)
        
        # Parse the meeting output
        with open(meeting_output_file, 'r') as f:
            meeting_text = f.read()
        
        meeting_data = self.process_meeting_output(meeting_text)
        
        # Find existing TO-DOs in the new sheet
        existing_todos = self.find_existing_todos(new_sheet)
        print(f"Found {len(existing_todos)} existing TO-DOs")
        
        # Get new TO-DOs from meeting
        new_todos_from_meeting = meeting_data.get('NEW TO-DOS', []) + meeting_data.get('TO-DO REVIEW', [])
        
        # Filter out duplicates
        truly_new_todos = []
        for new_todo in new_todos_from_meeting:
            is_duplicate = False
            for existing in existing_todos:
                if (new_todo.get('WHO', '').lower() == existing.get('WHO', '').lower() and
                    new_todo.get('TO-DO', '').lower() == existing.get('TO-DO', '').lower()):
                    is_duplicate = True
                    break
            if not is_duplicate:
                truly_new_todos.append(new_todo)
        
        print(f"Found {len(truly_new_todos)} truly new TO-DOs")
        
        # Add AI section with new items
        new_issues = meeting_data.get('ISSUES LIST (IDS)', [])
        self.add_ai_section(new_sheet, truly_new_todos, new_issues)
        
        # Save the workbook
        self.wb.save(self.workbook_path)
        print(f"Saved workbook with new sheet: {new_sheet.title}")
        
        return {
            'new_sheet_name': new_sheet.title,
            'next_date': next_date.strftime("%m/%d/%Y"),
            'new_todos_count': len(truly_new_todos),
            'new_issues_count': len(new_issues),
            'existing_todos_count': len(existing_todos)
        }

# Test function
def test_sheet_automation():
    """Test the sheet-based automation"""
    
    # Find an L10 workbook
    import os
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and 'populated' in f]
    
    if not excel_files:
        print("No populated L10 files found!")
        return
    
    # Use the most recent one
    excel_files.sort()
    workbook_file = excel_files[-1]
    
    print(f"Testing with workbook: {workbook_file}")
    
    # Create automation instance
    automation = L10SheetAutomation(workbook_file)
    
    # Process the meeting
    result = automation.create_next_l10_sheet('l10_output.txt', 'weekly')
    
    print("\n=== RESULTS ===")
    print(f"✓ Created new sheet: {result['new_sheet_name']}")
    print(f"✓ Next meeting date: {result['next_date']}")
    print(f"✓ Existing TO-DOs preserved: {result['existing_todos_count']}")
    print(f"✓ New TO-DOs added to AI section: {result['new_todos_count']}")
    print(f"✓ New Issues added to AI section: {result['new_issues_count']}")
    print(f"\nOpen {workbook_file} and check the new '{result['new_sheet_name']}' tab!")

if __name__ == "__main__":
    test_sheet_automation()