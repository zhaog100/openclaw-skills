#!/bin/bash

# Analyze bounty issues for new high-value tasks

echo "=== BOUNTY SCAN RESULTS ==="
echo "Current time: $(date)"
echo ""

# Get known issues
KNOWN_ISSUES=$(cat /home/zhaog/.openclaw/workspace/data/bounty-known-issues.txt | jq -r '.known_issues[]')

# Search for recent bounty issues (last 24 hours)
echo "Searching for bounty issues created in last 24 hours..."
RECENT_BOUNTIES=$(gh search issues "label:bounty created:>2026-04-13" --json number,repository,title,body,labels,createdAt,assignees --limit 50)

if [ $? -eq 0 ] && [ -n "$RECENT_BOUNTIES" ]; then
    echo "Found recent bounty issues:"
    NEW_UNASSIGNED_COUNT=0

    # Process each issue
    while IFS= read -r issue; do
        repo=$(echo "$issue" | jq -r '.repository.nameWithOwner')
        num=$(echo "$issue" | jq -r '.number')
        title=$(echo "$issue" | jq -r '.title')
        created=$(echo "$issue" | jq -r '.createdAt')
        assignees_count=$(echo "$issue" | jq -r '.assignees | length')

        # Check if unassigned
        if [ "$assignees_count" -eq 0 ]; then
            issue_key="$repo#$num"

            # Check if not in known issues
            if ! echo "$KNOWN_ISSUES" | grep -q "$issue_key"; then
                echo ""
                echo "🎯 NEW UNASSIGNED BOUNTY FOUND:"
                echo "   Repository: $repo"
                echo "   Issue #: $num"
                echo "   Title: $title"
                echo "   Created: $created"
                echo "   Issue URL: https://github.com/$repo/issues/$num"
                NEW_UNASSIGNED_COUNT=$((NEW_UNASSIGNED_COUNT + 1))

                # Check if repository is in blacklist
                BLACKLIST="SolFoundry/Scottcjn/rustchain/homelab-stack"
                if echo "$BLACKLIST" | grep -q "$repo"; then
                    echo "   ⚠️  SKIPPED: Repository in blacklist"
                else
                    # Extract bounty value from body (looking for dollar amounts)
                    body=$(echo "$issue" | jq -r '.body')
                    if echo "$body" | grep -q "\$[0-9]"; then
                        echo "   💰 Bounty: Contains monetary reward"
                        VALUE_SCORE=8  # High value if has dollar amount
                    else
                        echo "   📝 Bounty: Tutorial/content creation"
                        VALUE_SCORE=7  # Medium-high value for tutorials
                    fi

                    # Check if meets minimum score (≥7)
                    if [ "$VALUE_SCORE" -ge 7 ]; then
                        echo "   ✅ QUALIFIES: Value score ≥7 ($VALUE_SCORE)"
                    else
                        echo "   ❌ REJECTED: Value score <7 ($VALUE_SCORE)"
                    fi
                fi
            fi
        fi
    done <<< "$(echo "$RECENT_BOUNTIES" | jq -c '.[]')"

    if [ "$NEW_UNASSIGNED_COUNT" -eq 0 ]; then
        echo "No new unassigned bounty issues found in last 24 hours."
    fi
else
    echo "No recent bounty issues found or error occurred."
fi

echo ""
echo "=== SUMMARY ==="
echo "Scan completed at $(date)"