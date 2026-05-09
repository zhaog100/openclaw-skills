#!/bin/bash

echo "=== BOUNTY SCAN RESULTS ==="
echo "Current time: $(date)"
echo ""

# Get known issues
KNOWN_ISSUES=$(cat /home/zhaog/.openclaw/workspace/data/bounty-known-issues.txt | jq -r '.known_issues[]')

# Check if there are any unassigned bounty issues from last 24 hours
echo "Checking for new high-value bounty tasks..."

# Look through the recent bounty issues we found earlier
RECENT_BOUNTIES=$(gh search issues "label:bounty" --json number,repository,title,createdAt,assignees --limit 50)

if [ $? -eq 0 ]; then
    echo "Processing bounty issues..."

    # Count new unassigned issues that meet criteria
    NEW_COUNT=0

    while IFS= read -r issue; do
        repo=$(echo "$issue" | jq -r '.repository.nameWithOwner')
        num=$(echo "$issue" | jq -r '.number')
        created=$(echo "$issue" | jq -r '.createdAt')
        assignees_count=$(echo "$issue" | jq -r '.assignees | length')

        # Only consider issues from last 24 hours (created after 2026-04-13)
        if [[ "$created" > "2026-04-13T00:00:00Z" ]]; then
            if [ "$assignees_count" -eq 0 ]; then
                issue_key="$repo#$num"

                # Skip if already known
                if ! echo "$KNOWN_ISSUES" | grep -q "$issue_key"; then
                    # Skip blacklisted repos
                    BLACKLIST="SolFoundry/Scottcjn/rustchain/homelab-stack"
                    if ! echo "$BLACKLIST" | grep -q "$repo"; then
                        NEW_COUNT=$((NEW_COUNT + 1))
                    fi
                fi
            fi
        fi
    done <<< "$(echo "$RECENT_BOUNTIES" | jq -c '.[]')"

    if [ "$NEW_COUNT" -gt 0 ]; then
        echo ""
        echo "🎯 FOUND $NEW_COUNT NEW HIGH-VALUE BOUNTY TASK(S):"
        echo ""
        echo "Repository | Issue # | Title | Amount | Link"
        echo "-----------|---------|-------|--------|------"

        # Extract details for display
        while IFS= read -r issue; do
            repo=$(echo "$issue" | jq -r '.repository.nameWithOwner')
            num=$(echo "$issue" | jq -r '.number')
            title=$(echo "$issue" | jq -r '.title')
            created=$(echo "$issue" | jq -r '.createdAt')
            body=$(echo "$issue" | jq -r '.body')

            # Only process if from last 24 hours and unassigned
            if [[ "$created" > "2026-04-13T00:00:00Z" ]]; then
                assignees_count=$(echo "$issue" | jq -r '.assignees | length')
                if [ "$assignees_count" -eq 0 ]; then
                    issue_key="$repo#$num"

                    # Skip if known or blacklisted
                    if ! echo "$KNOWN_ISSUES" | grep -q "$issue_key"; then
                        BLACKLIST="SolFoundry/Scottcjn/rustchain/homelab-stack"
                        if ! echo "$BLACKLIST" | grep -q "$repo"; then
                            # Extract amount if present
                            amount=""
                            if echo "$body" | grep -q "\$[0-9]"; then
                                amount=$(echo "$body" | grep -o "\$[0-9]*[0-9,]*" | head -1 | sed 's/\$//' | tr -d ',')
                            fi

                            echo "$repo | $num | $title | ${amount:-Tutorial} | https://github.com/$repo/issues/$num"
                        fi
                    fi
                fi
            fi
        done <<< "$(echo "$RECENT_BOUNTIES" | jq -c '.[]')"
    else
        echo "No new high-value bounty tasks found in last 24 hours."
        echo "All recent bounty issues either have assignees, are from blacklisted repositories, or are already processed."
    fi
else
    echo "Error accessing GitHub bounty issues."
fi

echo ""
echo "=== SCAN COMPLETED ==="