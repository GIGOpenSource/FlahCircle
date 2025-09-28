# FlashCircle 项目部署文档
## 1. 项目介绍
FlashCircle 是一个基于 Django 和 PostgreSQL 的 Web 应用，本文档将指导你如何通过 Docker 快速部署该项目。
## 2. 环境要求
* 操作系统：Linux/macOS/Windows（推荐 Ubuntu 20.04+）
* Docker 版本：20.10 及以上
* Docker Compose 版本：2.0 及以上
* 网络：可访问互联网（用于拉取镜像和代码）
## 3. 部署步骤
### 3.1. 检查环境
```
确认 Docker 和 Docker Compose 已正确安装：
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker compose version
```
### 3.2. 获取代码
```
克隆代码仓库（替换为实际仓库地址）
git clone https://github.com/your-username/flashcircle.git
cd flashcircle
```

### 3.3. 配置说明
项目使用 docker-compose.yml 管理服务，主要包含两个服务：

* web：Django 应用服务（暴露端口 10080）
* db：PostgreSQL 数据库服务（暴露端口 5432）
```
* 默认配置信息：
* 数据库名称：flashc
* 数据库用户：flashc
* 数据库密码：flashc（生产环境请修改）
* Web 访问端口：10080
```
### 3.4. 启动服务
```
# 构建并启动容器（后台运行）
docker compose up -d

# 查看服务状态
docker compose ps
```
### 3.5. 验证部署

* Web 应用访问：http://服务器IP:10080
* 查看应用日志：docker compose logs -f web
* 查看数据库日志：docker compose logs -f db

## 4. 常用操作
```
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
```
## 5. 生产环境注意事项

### 5.1 安全配置：
1.修改数据库密码：
编辑 docker-compose.yml，将 db 和 web 服务下的 POSTGRES_PASSWORD=flashc 改为复杂密码（如 POSTGRES_PASSWORD=YourStrongPassword123!）。

2.限制 ALLOWED_HOSTS：
编辑 docker-compose.yml 中 web 服务的 ALLOWED_HOSTS=*，改为具体域名 / IP（如 ALLOWED_HOSTS=flashcircle.example.com,192.168.1.100），避免未授权访问。

3.关闭数据库端口暴露：
生产环境中，删除 db 服务下的 ports: - "5432:5432" 配置，仅允许 web 服务通过内部网络（flashc_net）访问数据库，防止外部直接连接数据库。

## 6. 联系方式

1. 邮箱：<yangborandesign@gmail.com>