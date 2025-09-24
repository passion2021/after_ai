#!/bin/bash

# 开发模式Docker脚本
echo "🐳 After AI 开发模式"
echo "================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 设置镜像名称和标签
IMAGE_NAME="after-ai"
TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"
CONTAINER_NAME="after-ai-dev"

# 检查是否已有同名容器在运行
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "⚠️  容器 $CONTAINER_NAME 已在运行"
    read -p "是否停止并重新启动？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 停止现有容器..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
    else
        echo "❌ 取消部署"
        exit 1
    fi
fi

# 创建日志目录
mkdir -p logs data

# 运行容器（开发模式）
echo "🚀 启动开发容器..."
docker run -d \
    --name $CONTAINER_NAME \
    -p 18000:18000 \
    -v $(pwd):/app \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/data:/app/data \
    --env-file .env \
    --restart unless-stopped \
    $FULL_IMAGE_NAME

if [ $? -eq 0 ]; then
    echo "✅ 开发容器启动成功"
    echo ""
    echo "📊 容器信息:"
    echo "  容器名称: $CONTAINER_NAME"
    echo "  镜像: $FULL_IMAGE_NAME"
    echo "  端口: 18000"
    echo "  源代码: 实时同步"
    echo "  日志目录: $(pwd)/logs"
    echo "  数据目录: $(pwd)/data"
    echo ""
    echo "🌐 访问地址:"
    echo "  应用: http://localhost:18000"
    echo "  API文档: http://localhost:18000/docs"
    echo ""
    echo "💡 开发模式特点:"
    echo "  ✅ 源代码实时同步，无需重新构建"
    echo "  ✅ 修改代码后自动重载"
    echo "  ✅ 日志实时输出到宿主机"
    echo ""
    echo "💡 管理命令:"
    echo "  查看日志: docker logs -f $CONTAINER_NAME"
    echo "  停止容器: docker stop $CONTAINER_NAME"
    echo "  重启容器: docker restart $CONTAINER_NAME"
    echo "  删除容器: docker rm $CONTAINER_NAME"
else
    echo "❌ 容器启动失败"
    exit 1
fi
