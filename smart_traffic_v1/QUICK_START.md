# 智能交通档案系统 - 快速开始指南

## 📋 目录结构

```
smart_traffic_v1/
├── backend/                    # Flask后端
│   ├── app/                    # 应用代码
│   ├── deploy/                 # 部署脚本
│   │   ├── deploy_server.sh   # 服务器部署脚本
│   │   └── db_init.sql        # 数据库初始化
│   ├── requirements.txt        # Python依赖
│   ├── run.py                 # 应用入口
│   └── DEPLOYMENT_GUIDE.md    # 详细部署指南
├── frontend/                   # Vue3前端（含预编译dist）
│   ├── src/                   # 源代码
│   ├── dist/                  # 预编译静态文件
│   ├── deploy_server.sh       # 服务器部署脚本
│   └── DEPLOYMENT_GUIDE.md    # 详细部署指南
├── ADR/                        # 架构决策记录
├── docs/                       # 文档
├── QUICK_START.md             # 本文件
└── README.md                  # 项目说明
```

## 💻 本地开发流程

### 1. 前端开发

```bash
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev

# 代码检查
npm run lint

# 生产构建
npm run build
```

### 2. 后端开发

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python run.py
```

## 🌐 部署工作流程

### 完整部署流程

```
本地开发 → 提交GitHub → 服务器拉取 → 前端部署 + 后端部署
```

### 详细步骤

#### 1. 本地开发提交

```bash
# 前端：构建生产版本
cd frontend
npm run build

# 提交所有变更
cd ..
git add .
git commit -m "feat: 描述你的更改"
git push origin main
```

#### 2. 服务器部署

**前端部署**（静态文件，无需Node.js）
```bash
ssh your-user@your-server-ip
cd /opt/smart_traffic_v1
git pull origin main
cd frontend
./deploy_server.sh
```

**后端部署**（Python + Gunicorn）
```bash
ssh your-user@your-server-ip
cd /opt/smart_traffic_v1
git pull origin main
cd backend/deploy
./deploy_server.sh
```

## 🔧 服务器首次设置

### 环境准备（Rocky Linux 9.6）

```bash
# 安装系统依赖
sudo dnf update -y
sudo dnf install -y git nginx python3 python3-venv python3-pip mariadb-server mariadb-devel

# 启动服务
sudo systemctl enable --now mariadb nginx

# 配置防火墙
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 创建项目目录
sudo mkdir -p /opt/smart_traffic_v1
sudo chown -R $USER:$USER /opt/smart_traffic_v1

# 克隆项目
cd /opt/smart_traffic_v1
git clone <你的GitHub仓库地址> .

# 设置执行权限
chmod +x frontend/deploy_server.sh
chmod +x backend/deploy/deploy_server.sh
```

## 📖 更多文档

- [前端部署指南](./frontend/DEPLOYMENT_GUIDE.md)
- [后端部署指南](./backend/DEPLOYMENT_GUIDE.md)
- [API文档](./docs/api-documentation.md)
- [架构决策](./ADR/)

## ⚠️ 注意事项

1. **前端**: dist目录已提交到Git，服务器无需Node.js
2. **后端**: 使用Gunicorn作为生产服务器
3. **数据库**: 需要提前配置MariaDB和创建数据库
4. **环境变量**: 记得配置 `.env` 文件中的敏感信息

## 🆘 故障排查

### 前端问题
```bash
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

### 后端问题
```bash
sudo systemctl status smart-traffic-backend
sudo journalctl -u smart-traffic-backend -f
tail -f /opt/smart_traffic_v1/logs/error.log
```

### 数据库问题
```bash
sudo systemctl status mariadb
mysql -u root -p
```
