#!/bin/bash

# 🔍 Monitor Copilot Security Warnings
# Run this script to check for firewall warnings in recent PRs

REPO_OWNER="Fadil369"
REPO_NAME="brainsait-unified-ecosystem"

echo "🔍 Checking recent PRs for Copilot firewall warnings..."

# Get recent PRs
recent_prs=$(gh pr list --repo "$REPO_OWNER/$REPO_NAME" --limit 10 --json number,title,body)

# Check for firewall warnings
echo "$recent_prs" | jq -r '.[] | select(.body | contains("blocked by the firewall")) | "PR #\(.number): \(.title)"'

# Check PR comments for warnings
echo "🔍 Checking PR comments for firewall warnings..."
gh pr list --repo "$REPO_OWNER/$REPO_NAME" --limit 5 --json number | jq -r '.[].number' | while read pr_number; do
    comments=$(gh pr view "$pr_number" --repo "$REPO_OWNER/$REPO_NAME" --comments --json comments)
    warnings=$(echo "$comments" | jq -r '.comments[] | select(.body | contains("blocked by the firewall")) | .body')
    if [ ! -z "$warnings" ]; then
        echo "⚠️  Firewall warning found in PR #$pr_number:"
        echo "$warnings"
        echo "---"
    fi
done

echo "✅ Security monitoring complete."
