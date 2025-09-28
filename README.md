FlashCircle 项目部署文档
项目介绍
FlashCircle 是一个基于 Django 和 PostgreSQL 的 Web 应用，本文档将指导你如何通过 Docker 快速部署该项目。
环境要求
操作系统：Linux/macOS/Windows（推荐 Ubuntu 20.04+）
Docker 版本：20.10 及以上
Docker Compose 版本：2.0 及以上
网络：可访问互联网（用于拉取镜像和代码）
部署步骤
1. 检查环境
确认 Docker 和 Docker Compose 已正确安装：
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker compose version
2. 获取代码
# 克隆代码仓库（替换为实际仓库地址）
git clone https://github.com/your-username/flashcircle.git
cd flashcircle
3. 配置说明
项目使用 docker-compose.yml 管理服务，主要包含两个服务：
web：Django 应用服务（暴露端口 10080）
db：PostgreSQL 数据库服务（暴露端口 5432）
默认配置信息：
数据库名称：flashc
数据库用户：flashc
数据库密码：flashc（生产环境请修改）
Web 访问端口：10080
4. 启动服务
# 构建并启动容器（后台运行）
docker compose up -d

# 查看服务状态
docker compose ps
5. 验证部署
Web 应用访问：http://服务器IP:10080
查看应用日志：docker compose logs -f web
查看数据库日志：docker compose logs -f db
常用操作
# 停止服务
docker compose down

# 重启服务
docker compose restart

# 进入 Web 容器
docker exec -it flashc_web /bin/sh

# 进入数据库容器
docker exec -it flahcicle_db /bin/sh

# 数据库连接（容器内）
psql -U flashc -d flashc

生产环境注意事项
安全配置：
修改数据库密码（POSTGRES_PASSWORD 环境变量）
限制 ALLOWED_HOSTS 为具体域名 / IP，不要使用 *
移除数据库端口暴露（5432:5432），仅通过内部网络访问
数据持久化：
数据库数据通过 pgdata 卷持久化，删除容器不会丢失数据
静态文件存储在 ./staticfiles 目录，确保目录权限正确
性能优化：
替换 runserver 为 Gunicorn 等生产级服务器
添加 Nginx 作为反向代理处理静态文件和请求转发
故障排查
服务启动失败：查看日志 docker compose logs
数据库连接问题：检查 POSTGRES_HOST=db 是否正确
端口冲突：修改 ports 配置中的宿主机端口（左侧数值）
迁移失败：进入 Web 容器执行 python manage.py migrate
联系方式
如有部署问题，请联系：support@flashcircle.example.com
