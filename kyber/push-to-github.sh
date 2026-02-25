#!/bin/bash
# KYBER → GitHub Push Script
# Run this from wherever you unzipped kyber-v1.0.bundle
# 
# STEP 1: Go to https://github.com/new → create repo "Kyber" under CryptoThaler
# STEP 2: Run this script

set -e

BUNDLE="kyber-v1.0.bundle"
REPO_URL="https://github.com/CryptoThaler/Kyber.git"
TARGET_DIR="kyber"

echo "🔷 KYBER GitHub Push"
echo "──────────────────────────────────────────"

# Clone from bundle into a clean directory
if [ -d "$TARGET_DIR" ]; then
  echo "Directory '$TARGET_DIR' already exists — pulling from bundle instead"
  cd "$TARGET_DIR"
  git fetch ../"$BUNDLE" main:main
  git checkout main
else
  git clone "$BUNDLE" "$TARGET_DIR"
  cd "$TARGET_DIR"
fi

# Point at real GitHub remote
git remote set-url origin "$REPO_URL" 2>/dev/null || git remote add origin "$REPO_URL"

echo ""
echo "Pushing to $REPO_URL ..."
git push -u origin main

echo ""
echo "✅ Done! Visit: https://github.com/CryptoThaler/Kyber"
