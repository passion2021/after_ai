#!/bin/bash

# PID文件路径
PID_FILE="./logs/uvicorn.pid"

# 检查PID文件是否存在
if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  PID文件不存在，可能服务未运行"
    echo "🔍 尝试查找并停止所有uvicorn进程..."
    
    # 查找所有uvicorn进程
    UVICORN_PIDS=$(pgrep -f "uvicorn main:app")
    if [ -z "$UVICORN_PIDS" ]; then
        echo "✅ 未找到运行中的uvicorn进程"
        exit 0
    else
        echo "找到uvicorn进程: $UVICORN_PIDS"
        echo "🛑 正在停止所有uvicorn进程..."
        pkill -f "uvicorn main:app"
        sleep 2
        
        # 检查是否还有残留进程
        REMAINING_PIDS=$(pgrep -f "uvicorn main:app")
        if [ -n "$REMAINING_PIDS" ]; then
            echo "⚠️  强制停止残留进程: $REMAINING_PIDS"
            pkill -9 -f "uvicorn main:app"
        fi
        
        echo "✅ 所有uvicorn进程已停止"
        exit 0
    fi
fi

# 读取PID
PID=$(cat "$PID_FILE")

# 检查进程是否存在
if ! ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  进程 $PID 不存在，可能已停止"
    echo "🧹 清理PID文件..."
    rm -f "$PID_FILE"
    exit 0
fi

echo "🛑 正在停止服务 (PID: $PID)..."

# 优雅停止
kill $PID

# 等待进程停止
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✅ 服务已优雅停止"
        rm -f "$PID_FILE"
        exit 0
    fi
    echo "⏳ 等待进程停止... ($i/10)"
    sleep 1
done

# 如果优雅停止失败，强制停止
echo "⚠️  优雅停止失败，强制停止进程..."
kill -9 $PID

# 再次检查
if ! ps -p $PID > /dev/null 2>&1; then
    echo "✅ 服务已强制停止"
    rm -f "$PID_FILE"
else
    echo "❌ 无法停止服务，请手动检查进程 $PID"
    exit 1
fi
