# 使用官方Python镜像
FROM python:3.11-slim

# 换源
RUN sed -i 's|http://deb.debian.org/debian|https://mirrors.aliyun.com/debian|g' /etc/apt/sources.list.d/debian.sources

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UPLOAD_FOLDER=/app/files
ENV MAX_FILE_SIZE_GB=2

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p /app/files

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]