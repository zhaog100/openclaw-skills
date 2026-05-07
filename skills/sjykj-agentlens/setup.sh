#!/usr/bin/env bash
# MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
# AgentLens Setup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== AgentLens Setup ==="

# Check Node.js
if ! command -v node &>/dev/null; then
  echo "❌ Node.js not found. Please install Node.js >= 18."
  exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ Node.js >= 18 required, found v$(node -v)"
  exit 1
fi
echo "✅ Node.js $(node -v)"

# Create data directory
mkdir -p data
echo "✅ Created data/"

# npm install
if [ ! -d node_modules ]; then
  echo "📦 Installing dependencies..."
  npm install --production
fi

# Verify better-sqlite3
node -e "const db = require('better-sqlite3'); console.log('✅ better-sqlite3 OK')" 2>/dev/null || {
  echo "❌ better-sqlite3 verification failed. Try: npm rebuild better-sqlite3"
  exit 1
}

echo ""
echo "=== AgentLens setup complete ==="
