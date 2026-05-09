#!/bin/bash

# Process bounty issues and find new high-value ones

echo "Processing bounty issues from last 24 hours..."

# Get known issues
KNOWN_ISSUES=$(cat /home/zhaog/.openclaw/workspace/data/bounty-known-issues.txt | jq -r '.known_issues[]')

# Search for recent bounty issues (last 24 hours)
RECENT_BOUNTIES=$(gh search issues "label:bounty created:>2026-04-13" --json number,repository,title,body,labels,createdAt,assignees --limit 50)

if [ $? -eq 0 ] && [ -n "$RECENT_BOUNTIES" ]; then
    echo "Found recent bounty issues:"
    echo "$RECENT_BOUNTIES" | jq -r '.[] | "\(.number) \(.repository.nameWithOwner) - \(.title)"'

    # Filter for unassigned issues and check if they're new
    NEW_UNASSIGNED=$(echo "$RECENT_BOUNTIES" | jq -r '.[] | select(.assignees == null) | .repository.nameWithOwner + "#" + (.number|tostring)' 2>/dev/null)

    if [ -n "$NEW_UNASSIGNED" ]; then
        # Check against known issues
        NEW_ISSUES=""
        while IFS= read -r issue; do
            if ! echo "$KNOWN_ISSUES" | grep -q "$issue"; then
                NEW_ISSUES="$NEW_ISSUES$issue\n"
            fi
        done <<< "$NEW_UNASSIGNED"

        if [ -n "$NEW_ISSUES" ]; then
            echo "New unassigned bounty issues found:"
            echo -e "$NEW_ISSUES"
            exit 0
        else
            echo "No new unassigned bounty issues found."
            exit 1
        fi
    else
        echo "No unassigned bounty issues found in last 24 hours."
        exit 1
    fi
else
    echo "No recent bounty issues found or error occurred."
    exit 1
fi