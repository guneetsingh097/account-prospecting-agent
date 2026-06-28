#!/usr/bin/env bash
# ============================================================
# Migraine Weather Alert — Mac mini setup
# ============================================================
# Installs a launchd agent that checks the barometric pressure
# forecast every 6 hours and sends native macOS notifications
# when a migraine-triggering pressure swing is coming.
#
# Usage:
#   bash setup_alerts_mac.sh "London"
#   bash setup_alerts_mac.sh "Toronto"
#   bash setup_alerts_mac.sh          # prompts for city
#
# To uninstall:
#   launchctl unload ~/Library/LaunchAgents/com.migrainetracker.alert.plist
#   rm ~/Library/LaunchAgents/com.migrainetracker.alert.plist
# ============================================================

set -euo pipefail

PLIST_NAME="com.migrainetracker.alert.plist"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$HOME/Library/LaunchAgents"
AGENT_PLIST="$AGENT_DIR/$PLIST_NAME"
TEMPLATE="$SCRIPT_DIR/launchd/$PLIST_NAME"
ALERT_SCRIPT="$SCRIPT_DIR/migraine_alert.py"

# ── Colours ──────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}!${NC} $*"; }
err()  { echo -e "${RED}✗${NC} $*" >&2; }

echo ""
echo "  🧠 Migraine Weather Alert — Mac mini Setup"
echo "  ─────────────────────────────────────────────"
echo ""
echo "  This sends proactive push notifications to your iPhone"
echo "  when a migraine-triggering pressure swing is forecast."
echo ""

# ── Non-interactive mode when args are provided ───────────────
# Arg $1 = city, $2 = ntfy topic (both optional — will prompt if missing)
CITY="${1:-}"
NTFY_TOPIC="${2:-}"
NON_INTERACTIVE=false
[[ -n "$CITY" ]] && NON_INTERACTIVE=true

# ── Get city ─────────────────────────────────────────────────
if [[ -z "$CITY" ]]; then
  read -r -p "  Enter your city name (e.g. London, Toronto, Chicago): " CITY
fi
if [[ -z "$CITY" ]]; then
  err "City name required."; exit 1
fi

# ── ntfy.sh topic for iPhone push ────────────────────────────
if [[ "$NON_INTERACTIVE" == "false" ]]; then
  echo ""
  echo "  ── iPhone push notifications ──────────────────────────"
  echo "  Uses ntfy.sh (free, no account needed)."
  echo ""
  echo "  Step 1: Install 'ntfy' on your iPhone (App Store)"
  echo "  Step 2: Choose a secret topic name — something hard to"
  echo "          guess, like:  migraine-$(openssl rand -hex 5 2>/dev/null || echo 'alerts-abc123')"
  echo ""
  read -r -p "  Enter your ntfy topic name (or press Enter to skip for now): " NTFY_TOPIC
  echo ""
fi

if [[ -z "$NTFY_TOPIC" ]]; then
  [[ "$NON_INTERACTIVE" == "false" ]] && warn "Skipping ntfy setup. Mac mini will show local notifications only."
  NTFY_TOPIC=""
fi

# ── Find Python 3 ────────────────────────────────────────────
PYTHON=""
for candidate in \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3 \
    /usr/bin/python3 \
    "$(command -v python3 2>/dev/null || true)"
do
  if [[ -x "$candidate" ]]; then
    PYTHON="$candidate"
    break
  fi
done

if [[ -z "$PYTHON" ]]; then
  err "Python 3 not found. Install it from https://python.org or via Homebrew: brew install python3"
  exit 1
fi
ok "Python: $PYTHON ($("$PYTHON" --version 2>&1))"

# ── Check requests is installed ───────────────────────────────
if ! "$PYTHON" -c "import requests" 2>/dev/null; then
  warn "'requests' not installed for $PYTHON. Installing now…"
  "$PYTHON" -m pip install requests --quiet
  ok "requests installed."
else
  ok "requests: available"
fi

# ── Check alert script exists ─────────────────────────────────
if [[ ! -f "$ALERT_SCRIPT" ]]; then
  err "Alert script not found at: $ALERT_SCRIPT"
  err "Run this setup from the project root directory."
  exit 1
fi
ok "Alert script: $ALERT_SCRIPT"

# ── Create plist from template ────────────────────────────────
mkdir -p "$AGENT_DIR"
sed \
  -e "s|__PYTHON__|$PYTHON|g" \
  -e "s|__SCRIPT__|$ALERT_SCRIPT|g" \
  -e "s|__HOME__|$HOME|g" \
  -e "s|__CITY__|$CITY|g" \
  -e "s|__NTFY_TOPIC__|$NTFY_TOPIC|g" \
  "$TEMPLATE" > "$AGENT_PLIST"
ok "Plist written: $AGENT_PLIST"

# ── Load the launchd agent ────────────────────────────────────
# Unload first in case it was already loaded (config change)
launchctl unload "$AGENT_PLIST" 2>/dev/null || true
launchctl load "$AGENT_PLIST"
ok "launchd agent loaded (com.migrainetracker.alert)"

echo ""
echo "  ─────────────────────────────────────────────"
ok "Setup complete! Checking every 6 hours for: ${YELLOW}${CITY}${NC}"

if [[ -n "$NTFY_TOPIC" ]]; then
  echo ""
  echo "  ── Finish iPhone setup ─────────────────────────────────"
  echo "  1. Open the ntfy app on your iPhone"
  echo "  2. Tap ＋ and subscribe to topic: ${YELLOW}${NTFY_TOPIC}${NC}"
  echo "  3. Allow notifications when prompted"
  echo "  That's it — you'll receive phone alerts automatically."
fi

echo ""
echo "  Notification schedule (per HIGH-risk event):"
echo "    📋  ~48h ahead  — plan tonight: sleep, hydrate, stock meds"
echo "    ⚠️   ~12h ahead  — start preventive protocol (breaks DND if urgent)"
echo "    🚨   Active now  — rescue medication alert (overrides Do Not Disturb)"
echo "    💛   MEDIUM risk ~24h ahead"
echo ""
echo "  Quick commands:"
echo "    Test push to phone:  ${YELLOW}python3 $ALERT_SCRIPT --test${NC}"
echo "    Run check now:       ${YELLOW}python3 $ALERT_SCRIPT${NC}"
echo "    View logs:           ${YELLOW}tail -f ~/Library/Logs/migraine_tracker.log${NC}"
echo "    Uninstall:           ${YELLOW}launchctl unload $AGENT_PLIST && rm $AGENT_PLIST${NC}"
echo ""

# ── Run a test notification right now ────────────────────────
echo "  Sending a test notification to confirm everything works…"
"$PYTHON" "$ALERT_SCRIPT" --test
echo ""
ok "Done. You'll get your first real check within 6 hours, or run the script manually."
echo ""
