#!/usr/bin/env bash
# ==============================================================================
# SeaVision AI - Quickstart Full-Stack Launcher (SIH26143)
# ==============================================================================

set -e

PORT=${PORT:-8000}

echo "======================================================================"
echo "🌊 Launching SeaVision AI Full-Stack Platform..."
echo "======================================================================"

# Ensure Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is required but not installed."
    exit 1
fi

echo "🚀 Starting Full-Stack Server on port ${PORT}..."
echo "🛰️  Tactical Maritime Command Center: http://localhost:${PORT}/"
echo "📡 REST API Endpoint:               http://localhost:${PORT}/api/v1/spill-analysis"
echo "======================================================================"

# Try to open in browser if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    (sleep 1 && open "http://localhost:${PORT}/") &
elif command -v xdg-open &> /dev/null; then
    (sleep 1 && xdg-open "http://localhost:${PORT}/") &
fi

exec python3 server.py "$PORT"
