#!/bin/bash

# 简化的Docker停止脚本
echo "🛑 After AI 容器停止脚本"
echo "================================"

CONTAINER_NAME="after-ai-app"

# 检查容器是否存在
if ! docker ps -a -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "⚠️  容器 $CONTAINER_NAME 不存在"
    exit 0
fi

# 检查容器是否在运行
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "🛑 停止容器: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME
    
    if [ $? -eq 0 ]; then
        echo "✅ 容器已停止"
    else
        echo "❌ 停止容器失败"
        exit 1
    fi
else
    echo "⚠️  容器 $CONTAINER_NAME 未在运行"
fi

# 询问是否删除容器
read -p "是否删除容器？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  删除容器: $CONTAINER_NAME"
    docker rm $CONTAINER_NAME
    
    if [ $? -eq 0 ]; then
        echo "✅ 容器已删除"
    else
        echo "❌ 删除容器失败"
        exit 1
    fi
fi

echo "✅ 操作完成"
