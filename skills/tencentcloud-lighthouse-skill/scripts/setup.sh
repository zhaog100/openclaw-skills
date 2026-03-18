#!/usr/bin/env bash
set -euo pipefail

# Lighthouse MCP Setup — installs mcporter (if needed) and writes config
# Usage:
#   setup.sh --secret-id <ID> --secret-key <KEY> [--config-path <path>] [--check-only]
#   setup.sh --check-only
#
# Environment variables (highest priority):
#   TENCENTCLOUD_SECRET_ID, TENCENTCLOUD_SECRET_KEY
#
# Config file: {skill_dir}/config.json (env vars take precedence)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_CONFIG="$SKILL_DIR/config.json"

# Defaults
MCPORTER_CONFIG="${HOME}/.mcporter/mcporter.json"
DEFAULT_REGION="ap-guangzhou"

# Load skill config if exists
if [[ -f "$SKILL_CONFIG" ]]; then
  MCPORTER_CONFIG="$(node -e "
    const c = JSON.parse(require('fs').readFileSync('$SKILL_CONFIG','utf8'));
    console.log(c.mcporter?.configPath || '$MCPORTER_CONFIG'.replace(/^~/, process.env.HOME));
  " 2>/dev/null || echo "$MCPORTER_CONFIG")"
  MCPORTER_CONFIG="${MCPORTER_CONFIG/#\~/$HOME}"
  DEFAULT_REGION="$(node -e "
    const c = JSON.parse(require('fs').readFileSync('$SKILL_CONFIG','utf8'));
    console.log(c.lighthouse?.defaultRegion || '$DEFAULT_REGION');
  " 2>/dev/null || echo "$DEFAULT_REGION")"
fi

# CLI args (lower priority than env vars)
SECRET_ID=""
SECRET_KEY=""
CHECK_ONLY=false

usage() {
  cat >&2 <<'EOF'
Usage:
  setup.sh --secret-id <ID> --secret-key <KEY> [--config-path <path>] [--check-only]
  setup.sh --check-only

Priority (high → low): env vars > CLI args > config.json

Options:
  --secret-id     Tencent Cloud SecretId
  --secret-key    Tencent Cloud SecretKey
  --config-path   mcporter config file path (default from config.json or ~/.mcporter/mcporter.json)
  --check-only    Only check if mcporter and config are ready
  -h, --help      Show this help
EOF
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --secret-id)   SECRET_ID="${2:-}";   shift 2 ;;
    --secret-key)  SECRET_KEY="${2:-}";  shift 2 ;;
    --config-path) MCPORTER_CONFIG="${2:-}"; shift 2 ;;
    --check-only)  CHECK_ONLY=true;      shift   ;;
    -h|--help)     usage ;;
    *)             echo "Unknown arg: $1" >&2; usage ;;
  esac
done

# Resolve env vars from config.json if CLI args not provided
if [[ -z "$SECRET_ID" && -f "$SKILL_CONFIG" ]]; then
  SECRET_ID="$(node -e "
    const c = JSON.parse(require('fs').readFileSync('$SKILL_CONFIG','utf8'));
    console.log(c.env?.TENCENTCLOUD_SECRET_ID || '');
  " 2>/dev/null || echo "")"
fi
if [[ -z "$SECRET_KEY" && -f "$SKILL_CONFIG" ]]; then
  SECRET_KEY="$(node -e "
    const c = JSON.parse(require('fs').readFileSync('$SKILL_CONFIG','utf8'));
    console.log(c.env?.TENCENTCLOUD_SECRET_KEY || '');
  " 2>/dev/null || echo "")"
fi

# Environment variables override everything
SECRET_ID="${TENCENTCLOUD_SECRET_ID:-$SECRET_ID}"
SECRET_KEY="${TENCENTCLOUD_SECRET_KEY:-$SECRET_KEY}"

# --- Check mode ---
if $CHECK_ONLY; then
  echo "=== Lighthouse MCP Status Check ==="
  echo "Config path: $MCPORTER_CONFIG"
  echo "Default region: $DEFAULT_REGION"

  command -v mcporter &>/dev/null && echo "[OK] mcporter: $(mcporter --version 2>/dev/null || echo 'ok')" || echo "[MISSING] mcporter (npm install -g mcporter)"

  if [[ -f "$MCPORTER_CONFIG" ]]; then
    echo "[OK] Config file: $MCPORTER_CONFIG"
    grep -q '"lighthouse"' "$MCPORTER_CONFIG" 2>/dev/null && echo "[OK] lighthouse MCP configured" || echo "[MISSING] lighthouse MCP not in config"
  else
    echo "[MISSING] Config file: $MCPORTER_CONFIG"
  fi

  if command -v mcporter &>/dev/null && [[ -f "$MCPORTER_CONFIG" ]]; then
    echo "" && echo "=== MCP Servers ==="
    mcporter list --config "$MCPORTER_CONFIG" 2>/dev/null || echo "[ERROR] Failed to list servers"
  fi
  exit 0
fi

# --- Setup mode ---
if [[ -z "$SECRET_ID" ]]; then echo "[ERROR] SecretId required (env TENCENTCLOUD_SECRET_ID or --secret-id)" >&2; exit 1; fi
if [[ -z "$SECRET_KEY" ]]; then echo "[ERROR] SecretKey required (env TENCENTCLOUD_SECRET_KEY or --secret-key)" >&2; exit 1; fi

echo "=== Lighthouse MCP Auto Setup ==="

# Install mcporter if needed
if command -v mcporter &>/dev/null; then
  echo "[OK] mcporter installed"
else
  echo "[INSTALL] Installing mcporter..."
  npm install -g mcporter
  command -v mcporter &>/dev/null || { echo "[ERROR] mcporter install failed" >&2; exit 1; }
  echo "[OK] mcporter installed"
fi

# Ensure config dir exists
CONFIG_DIR="$(dirname "$MCPORTER_CONFIG")"
[[ -d "$CONFIG_DIR" ]] || { mkdir -p "$CONFIG_DIR" && echo "[OK] Created: $CONFIG_DIR"; }

# Write config
TEMP_CONFIG="$(mktemp)"
node -e "
  const fs = require('fs');
  let config = {};
  try { config = JSON.parse(fs.readFileSync('$MCPORTER_CONFIG', 'utf8')); } catch {}
  if (!config.mcpServers) config.mcpServers = {};
  config.mcpServers.lighthouse = {
    command: 'npx',
    args: ['-y', 'lighthouse-mcp-server'],
    env: {
      TENCENTCLOUD_SECRET_ID: '$SECRET_ID',
      TENCENTCLOUD_SECRET_KEY: '$SECRET_KEY'
    }
  };
  fs.writeFileSync('$TEMP_CONFIG', JSON.stringify(config, null, 2));
"
mv "$TEMP_CONFIG" "$MCPORTER_CONFIG"
echo "[OK] Config written: $MCPORTER_CONFIG"

# Verify
echo "" && echo "=== Verification ==="
mcporter list --config "$MCPORTER_CONFIG" 2>/dev/null || true
if mcporter list lighthouse --config "$MCPORTER_CONFIG" --schema 2>/dev/null; then
  echo "" && echo "[OK] Setup complete!"
else
  echo "[WARN] Tools not yet listed (normal on first run)"
fi
echo "Config: $MCPORTER_CONFIG | Region: $DEFAULT_REGION"
