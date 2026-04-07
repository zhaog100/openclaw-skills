#!/usr/bin/env python3
import json
import sys

# Read the JSON response
with open('issues.json', 'r') as f:
    issues = json.load(f)

# Filter out pull requests (which have pull_request key)
filtered_issues = [issue for issue in issues if 'pull_request' not in issue]

# Display issues
for issue in filtered_issues:
    print(f"{issue['number']}: {issue['title']}")

print(f"\nTotal issues found: {len(filtered_issues)}")