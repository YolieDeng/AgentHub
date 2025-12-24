#!/bin/bash

# AgentHub 部署脚本

set -e

APP_DIR="$(dirname "$0")"
LOG_FILE="$APP_DIR/server.log"

echo "🚀 开始部署 AgentHub..."
cd "$APP_DIR"

# 1. 同步依赖
echo "📦 同步依赖..."
uv sync

# 2. 停止旧进程
echo "🔍 检查程序状态..."
PYTHON_PID=$(pgrep -f "uvicorn app.main:app" || echo "")

if [ ! -z "$PYTHON_PID" ]; then
    echo "⚠️  停止旧进程 (PID: $PYTHON_PID)..."
    kill -TERM $PYTHON_PID 2>/dev/null || true
    sleep 3
    kill -KILL $PYTHON_PID 2>/dev/null || true
    echo "✅ 已停止"
fi

# 3. 启动程序（使用 screen）
echo "🚀 启动程序..."
screen -dmS agenthub bash -c "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 2>&1 | tee $LOG_FILE"

sleep 3

if screen -list | grep -q "agenthub"; then
    echo "🎉 部署完成！"
    echo "📝 进入会话: screen -r agenthub"
    echo "📝 日志文件: tail -f $LOG_FILE"
    echo "🔗 地址: http://localhost:8000"
else
    echo "❌ 启动失败，查看日志: tail -f $LOG_FILE"
    exit 1
fi
