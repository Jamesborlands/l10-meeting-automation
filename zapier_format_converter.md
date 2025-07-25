# Zapier Format Converter

Since Render is having deployment issues, here's how to convert your Zapier JSON to the working L10 format:

## Your Current Zapier Format:
```json
{
  "new_commitments": [...],
  "issues_discussed": [...],
  "todo_review": [...]
}
```

## Convert to Working L10 Format:
```json
{
  "NEW TO-DOS": [
    {
      "WHO": "Person Name",
      "TO-DO": "Task description", 
      "DUE DATE": "Due date",
      "CONTEXT": "Context info",
      "DEPENDENCIES": "Dependencies"
    }
  ],
  "ISSUES LIST (IDS)": [
    {
      "issue_description": "Issue description",
      "who_raised_it": "Person Name",
      "root_cause": "Root cause",
      "related_discussions": "Discussion points",
      "notes": "Additional notes"
    }
  ]
}
```

## Mapping:
- `new_commitments[].who` → `NEW TO-DOS[].WHO`
- `new_commitments[].task` → `NEW TO-DOS[].TO-DO` 
- `new_commitments[].due_date` → `NEW TO-DOS[].DUE DATE`
- `issues_discussed[].issue` → `ISSUES LIST (IDS)[].issue_description`
- `issues_discussed[].raised_by` → `ISSUES LIST (IDS)[].who_raised_it`