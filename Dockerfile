# 基础镜像：Python 3.11轻量版（适配Django 4.x/5.x，体积小）
FROM python:3.11-slim

# 环境变量：禁止生成.pyc文件+实时打印日志
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 工作目录（容器内的项目根目录）
WORKDIR /app

# 安装系统依赖（PostgreSQL驱动需要的编译工具）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*  # 清理缓存减小镜像体积

# 复制Python依赖文件→安装依赖（利用Docker缓存，改代码不重新装依赖）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个Django项目到容器
COPY . .

# 创建静态文件目录（与docker-compose中的staticfiles卷匹配）
RUN mkdir -p /app/staticfiles && \
    chmod -R 755 /app/staticfiles  # 授权避免Nginx读不到

# 暴露后端端口（与docker-compose一致）
EXPOSE 8000

# 启动命令（开发环境用，docker-compose的command会覆盖，可留空）
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]