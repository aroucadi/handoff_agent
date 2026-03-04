#!/bin/bash
# ─────────────────────────────────────────────────────
# Synapse — Start Local Development Environment
#
# Starts all 4 services in the background:
# 1. CRM Simulator Backend (:8001)
# 2. Graph Generator (:8002)
# 3. Synapse API (:8000)
# 4. Synapse Voice UI (:5174)
# 5. CRM Simulator Frontend (:5173)
# ─────────────────────────────────────────────────────

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║      SYNAPSE — Starting All Services         ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Start CRM Simulator Backend
echo "🚀 Starting CRM Simulator Backend on :8001..."
cd "$ROOT_DIR/crm-simulator"
uvicorn main:app --host 0.0.0.0 --port 8001 &
CRM_PID=$!

# Start Graph Generator
echo "🚀 Starting Graph Generator on :8002..."
cd "$ROOT_DIR/graph-generator"
uvicorn main:app --host 0.0.0.0 --port 8002 &
GEN_PID=$!

# Start Synapse API
echo "🚀 Starting Synapse API on :8000..."
cd "$ROOT_DIR/backend"
uvicorn main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Start Hub API
echo "🚀 Starting Hub API on :8003..."
cd "$ROOT_DIR/hub/api"
uvicorn main:app --host 0.0.0.0 --port 8003 &
HUB_API_PID=$!

# Start Synapse Voice UI
echo "🚀 Starting Voice UI on :5174..."
cd "$ROOT_DIR/frontend"
npm run dev &
UI_PID=$!

# Start CRM Frontend
echo "🚀 Starting CRM Frontend on :5173..."
cd "$ROOT_DIR/crm-simulator/frontend"
npm run dev &
CRM_UI_PID=$!

# Start Hub Frontend
echo "🚀 Starting Hub Frontend on :5176..."
cd "$ROOT_DIR/hub"
npm run dev -- --port 5176 &
HUB_UI_PID=$!

echo ""
echo "═══════════════════════════════════════════════"
echo "  All services started!"
echo ""
echo "  🏢 CRM Simulator:   http://localhost:5173"
echo "  🎙️ Synapse Voice:    http://localhost:5174"
echo "  🌉 Synapse Hub:      http://localhost:5176"
echo "  📡 Backend API:      http://localhost:8000/health"
echo "  ⚙️  Graph Generator:  http://localhost:8002/health"
echo "  🛠️  Hub API:         http://localhost:8003/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "═══════════════════════════════════════════════"

# Wait and cleanup on Ctrl+C
cleanup() {
    echo ""
    echo "Stopping all services..."
    kill $CRM_PID $GEN_PID $API_PID $HUB_API_PID $UI_PID $CRM_UI_PID $HUB_UI_PID 2>/dev/null
    echo "All services stopped."
}
trap cleanup EXIT
wait
