#!/bin/bash
# JARVIS AI - Auto-push to GitHub

echo "========================================"
echo "  JARVIS AI - Git Auto-Push"
echo "========================================"

cd /workspaces/jarvis-ai

# Check for changes
if git status --porcelain | grep -q .; then
    echo "Changes detected, committing..."
    git add -A
    git commit -m "JARVIS: Auto-update $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Pushing to remote..."
    git push origin main 2>&1 || git push origin master 2>&1
    echo "✅ Code pushed to GitHub"
else
    echo "No changes to commit"
fi

echo ""
echo "Latest commits:"
git log --oneline -5