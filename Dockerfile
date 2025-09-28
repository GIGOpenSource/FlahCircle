# 使用 Python 3.11 基础镜像适配 Django 5.2
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=ClipAI.settings

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装 Python 依赖
COPY req.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建静态文件和媒体文件目录
RUN mkdir -p staticfiles media

# 暴露 Django 开发服务器端口
EXPOSE 8000

# 启动命令（与 docker-compose.yml 中一致）
CMD sh -c "find . -path '*/migrations/*.py' -not -name '__init__.py' -delete && \
    find . -path '*/migrations/*.pyc' -delete && \
    python manage.py makemigrations && \
    python manage.py migrate --noinput && \
    python manage.py runserver 0.0.0.0:8000"
