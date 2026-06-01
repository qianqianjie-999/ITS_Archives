# 前端部署工作流程指南

## 概述

本指南描述了智能交通档案系统的前端开发部署工作流程：

```
本地开发 → 本地编译 → 提交dist到GitHub → 服务器Pull → 部署生效
```

**关键特点**：服务器端**无需安装 Node.js**，直接部署预编译的静态文件。

## 本地开发环境配置

### 1. 开发环境要求

- Node.js 20.x 或更高版本
- npm 包管理器

### 2. 本地开发命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 代码检查
npm run lint

# 生产构建（生成dist目录）
npm run build
```

## GitHub 工作流程

### 1. Git 配置

```bash
# 设置用户信息
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

### 2. 开发提交流程（包含编译产物）

```bash
# 1. 修改代码后，构建生产版本
npm run build

# 2. 查看变更（确保dist目录包含在内）
git status

# 3. 添加所有变更（包括dist目录）
git add .

# 4. 提交变更（使用有意义的提交信息）
git commit -m "feat: 添加新功能"

# 5. 推送到GitHub
git push origin main
```

### 3. 推荐的提交信息规范

- `feat:` 新功能
- `fix:` 修复Bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具链

## 服务器部署（Rocky Linux 9.6）

### 服务器要求

- **无需 Node.js**（静态文件直接部署）
- 需要 Git（用于拉取代码）
- 需要 Nginx（用于静态文件服务）

### 1. 首次部署

```bash
# 登录服务器
ssh user@your-server-ip

# 安装必要依赖
sudo dnf install -y git nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# 创建项目目录
sudo mkdir -p /opt/smart_traffic_v1
sudo chown -R $USER:$USER /opt/smart_traffic_v1

# 克隆仓库
cd /opt/smart_traffic_v1
git clone <你的GitHub仓库地址> .

# 运行部署脚本
cd frontend
chmod +x deploy_server.sh
./deploy_server.sh
```

### 2. 日常更新部署

```bash
# 登录服务器
ssh user@your-server-ip

# 进入项目目录
cd /opt/smart_traffic_v1

# 拉取最新代码（包含预编译的dist）
git pull origin main

# 运行部署脚本
cd frontend
./deploy_server.sh
```

## 服务器部署脚本说明

### deploy_server.sh 功能

该脚本会自动完成以下操作：

1. ✅ 检查/安装 Git
2. ✅ 从 GitHub 拉取最新代码
3. ✅ 验证 dist 目录存在
4. ✅ 备份当前版本
5. ✅ 部署静态文件到 Nginx 目录
6. ✅ 配置 Nginx（首次）
7. ✅ 重启 Nginx 服务

## 目录结构

```
smart_traffic_v1/
├── frontend/
│   ├── src/              # 源代码
│   ├── dist/             # 构建输出（已提交到Git）
│   ├── package.json
│   ├── deploy_server.sh  # 服务器部署脚本
│   └── DEPLOYMENT_GUIDE.md
└── backend/
```

## 注意事项

1. **dist 目录**：构建产物已配置为提交到 Git（.gitignore 中已注释）
2. **Node.js 版本**：确保本地开发环境使用兼容的 Node.js 版本（推荐 20.x）
3. **权限问题**：确保部署脚本有执行权限 `chmod +x deploy_server.sh`
4. **Nginx 配置**：根据实际情况修改服务器名称和端口配置

## 故障排查

### 构建失败（本地）
```bash
# 清理 node_modules 重新安装
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 部署失败（服务器）
```bash
# 检查 dist 目录是否存在
ls -la /opt/smart_traffic_v1/frontend/dist

# 检查 Nginx 配置语法
sudo nginx -t

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log
```

### Git 拉取失败
```bash
# 检查网络连接
ping github.com

# 检查仓库配置
git remote -v
```
