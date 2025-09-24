#!/bin/bash

# 日志目录设置为当前路径下 logs 文件夹
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

# 初始化 pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# 切换到 after_ai 虚拟环境
pyenv activate after_ai

# 检查是否已有进程在运行
PID_FILE="./logs/uvicorn.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  服务已在运行 (PID: $PID)"
        echo "如需重启，请先运行 ./stop.sh"
        exit 1
    else
        echo "清理旧的PID文件..."
        rm -f "$PID_FILE"
    fi
fi

# 启动 uvicorn 到后台，并将输出写入日志
echo "🚀 启动 uvicorn 到后台..."
nohup uvicorn main:app --host 0.0.0.0 --port 18000 --reload > "$LOG_DIR/uvicorn.out" 2>&1 &
UVICORN_PID=$!

# 保存PID到文件
echo $UVICORN_PID > "$PID_FILE"

# 等待几秒检查服务是否正常启动
sleep 3
if ps -p $UVICORN_PID > /dev/null 2>&1; then
    echo "✅ uvicorn 已在后台运行 (PID: $UVICORN_PID)"
    echo "📝 日志写入: $LOG_DIR/uvicorn.out"
    echo "🌐 服务地址: http://localhost:18000"
    echo "📖 API文档: http://localhost:18000/docs"
    echo ""
    echo "💡 使用 ./stop.sh 停止服务"
else
    echo "❌ 服务启动失败，请检查日志: $LOG_DIR/uvicorn.out"
    rm -f "$PID_FILE"
    exit 1
fi
