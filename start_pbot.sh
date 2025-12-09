#!/bin/bash
# start_pbot.sh - Startar backend + Cloudflare-tunnel för testning

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
KUZU_LOCK="$PROJECT_ROOT/ai-services/storage/index/kuzu/.lock"

echo "🚀 Startar Adda P-Bot testmiljö..."

# 1. Ta bort Kuzu-lås om det finns
if [ -f "$KUZU_LOCK" ]; then
    echo "🔓 Tar bort Kuzu-lås..."
    rm -f "$KUZU_LOCK"
fi

# 2. Rensa Python-cache
echo "🧹 Rensar Python-cache..."
find "$PROJECT_ROOT/ai-services" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 3. Starta Cloudflare-tunnel (i bakgrunden)
echo "☁️  Startar Cloudflare-tunnel..."
cloudflared tunnel --url http://localhost:5000 &
TUNNEL_PID=$!
echo "   Tunnel PID: $TUNNEL_PID"

# 4. Starta backend (i förgrunden)
echo "🐍 Startar backend-server..."
cd "$PROJECT_ROOT/ai-services"
source venvP312/bin/activate
python server.py

# Cleanup vid Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Stänger tunnel..."
    kill $TUNNEL_PID 2>/dev/null || true
    echo "✅ Klart!"
}
trap cleanup EXIT

