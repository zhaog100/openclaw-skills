#!/bin/bash
# PR Monitor - v7.4
LOG_FILE="/tmp/pr_monitor_$(date +%H).log"

echo "[$(date)] Checking PR status..." >> $LOG_FILE
cd ~/.openclaw/workspace/skills/github-bounty-hunter

# Check open PRs
gh pr list --author @me --state open --json number,title,url,updatedAt >> $LOG_FILE 2>&1

echo "[$(date)] PR monitoring completed" >> $LOG_FILE
