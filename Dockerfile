# 使用Python 3.11官方镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --timeout 1000 --retries 5 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

# 复制项目文件
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 18000

# 健康检查（使用Python内置的urllib）
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:18000/docs')" || exit 1

# 启动命令（支持开发模式）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "18000", "--reload"]
