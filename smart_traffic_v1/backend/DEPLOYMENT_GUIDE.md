# 后端部署工作流程指南

## 概述

本指南描述了智能交通档案系统后端的部署工作流程：

```
GitHub拉取 → 虚拟环境 → 安装依赖 → 数据库初始化 → Gunicorn启动
```

**关键特点**：
- 使用 Gunicorn 作为生产环境 WSGI 服务器
- 部署脚本自动初始化数据库
- 自动创建系统用户（admin/editor/viewer）

## 服务器环境要求

- Rocky Linux 9.6
- Python 3.8+
- MariaDB/MySQL 数据库
- Nginx（反向代理）
- Git

## 部署步骤

### 首次部署

```bash
# 1. 登录服务器
ssh user@your-server-ip

# 2. 安装系统依赖
sudo dnf install -y python3 python3-venv python3-pip git mariadb-server mariadb-devel nginx

# 3. 创建项目目录
sudo mkdir -p /opt/smart_traffic_v1
sudo chown -R $USER:$USER /opt/smart_traffic_v1

# 4. 克隆GitHub仓库
cd /opt/smart_traffic_v1
git clone <你的GitHub仓库地址> .

# 5. 运行部署脚本（自动完成：虚拟环境、依赖安装、数据库初始化）
cd backend/deploy
chmod +x deploy_server.sh
sudo ./deploy_server.sh

# 6. 编辑环境配置（修改数据库密码和密钥）
sudo nano /opt/smart_traffic_v1/.env
```

### 日常更新部署

```bash
# 1. 登录服务器
ssh user@your-server-ip

# 2. 进入项目目录
cd /opt/smart_traffic_v1

# 3. 拉取最新代码
git pull origin main

# 4. 运行部署脚本
cd backend/deploy
sudo ./deploy_server.sh
```

## 部署脚本功能

### deploy_server.sh

该脚本自动完成以下操作：

1. ✅ 检查/安装 Git
2. ✅ 拉取最新代码
3. ✅ 检查/安装 Python 环境
4. ✅ 创建/更新虚拟环境
5. ✅ 安装 Python 依赖（包含 gunicorn）
6. ✅ 启动 MariaDB 服务
7. ✅ 执行数据库初始化脚本（创建表、索引、初始用户）
8. ✅ 创建必要的目录（uploads, logs）
9. ✅ 配置 systemd 服务
10. ✅ 启动 Gunicorn 服务

## Gunicorn 配置

部署脚本使用以下 Gunicorn 配置：

- **工作进程数**: 4
- **绑定地址**: 127.0.0.1:5000
- **超时时间**: 120秒
- **访问日志**: `/opt/smart_traffic_v1/logs/access.log`
- **错误日志**: `/opt/smart_traffic_v1/logs/error.log`

## 服务管理

```bash
# 查看服务状态
sudo systemctl status smart-traffic-backend

# 查看实时日志
sudo journalctl -u smart-traffic-backend -f

# 重启服务
sudo systemctl restart smart-traffic-backend

# 停止服务
sudo systemctl stop smart-traffic-backend

# 查看应用日志
tail -f /opt/smart_traffic_v1/logs/error.log
```

## 环境配置

环境配置文件位于: `/opt/smart_traffic_v1/.env`

重要配置项：

```bash
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_USER=smart_traffic
DB_PASSWORD=your_db_password
DB_NAME=smart_traffic
UPLOAD_FOLDER=/opt/smart_traffic_v1/uploads
PORT=5000
DEBUG=False
```

## 故障排查

### 服务启动失败

```bash
# 1. 检查服务状态
sudo systemctl status smart-traffic-backend

# 2. 查看错误日志
sudo journalctl -u smart-traffic-backend -n 50

# 3. 检查虚拟环境
source /opt/smart_traffic_v1/venv/bin/activate
cd /opt/smart_traffic_v1/backend
python run.py  # 手动运行查看错误
```

### 数据库连接问题

```bash
# 1. 检查数据库服务
sudo systemctl status mariadb

# 2. 测试数据库连接
mysql -u smart_traffic -p smart_traffic

# 3. 检查.env中的数据库配置
cat /opt/smart_traffic_v1/.env
```

### Nginx 反向代理问题

```bash
# 1. 检查 Nginx 配置
sudo nginx -t

# 2. 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log

# 3. 重启 Nginx
sudo systemctl restart nginx
```

## 目录结构

```
/opt/smart_traffic_v1/
├── backend/              # 后端代码
│   ├── app/              # 应用代码
│   ├── deploy/           # 部署脚本
│   │   ├── deploy_server.sh
│   │   └── db_init.sql
│   ├── requirements.txt
│   └── run.py
├── venv/                # Python 虚拟环境
├── uploads/             # 上传文件目录
├── logs/                # 日志目录
│   ├── access.log
│   └── error.log
└── .env                 # 环境配置文件
```
