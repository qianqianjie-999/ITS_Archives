#!/bin/bash
# ==============================================
# 智能交通档案系统 - 前端部署脚本（静态文件版本）
# 适用环境: Rocky Linux 9.6
# 功能: 从GitHub拉取预编译的dist目录 → 直接部署到Nginx
# 无需Node.js，无需编译！
# ==============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置参数
APP_DIR="/opt/smart_traffic_frontend"
NGINX_CONF="/etc/nginx/conf.d/smart-traffic-frontend.conf"
BACKUP_DIR="/opt/smart_traffic_frontend_backup"
GIT_REPO_DIR="/opt/smart_traffic_v1"  # Git仓库目录

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}智能交通档案系统 - 前端部署脚本${NC}"
echo -e "${YELLOW}模式: 静态文件部署（无需Node.js）${NC}"
echo -e "${YELLOW}==============================================${NC}"

# 1. 检查Git
echo -e "${GREEN}[1/5] 检查Git环境...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git未安装，正在安装...${NC}"
    dnf install -y git
fi
echo -e "${GREEN}Git版本: $(git --version)${NC}"

# 2. 拉取最新代码
echo -e "${GREEN}[2/5] 拉取最新代码...${NC}"
cd $GIT_REPO_DIR
git pull origin main

# 3. 检查dist目录
echo -e "${GREEN}[3/5] 检查dist目录...${NC}"
DIST_DIR="$GIT_REPO_DIR/frontend/dist"
if [ ! -d "$DIST_DIR" ] || [ -z "$(ls -A "$DIST_DIR")" ]; then
    echo -e "${RED}错误: dist目录不存在或为空！${NC}"
    echo -e "${RED}请先在本地运行 'npm run build' 并提交dist目录到GitHub${NC}"
    exit 1
fi
echo -e "${GREEN}dist目录内容:${NC}"
ls -la "$DIST_DIR"

# 4. 备份当前版本
echo -e "${GREEN}[4/5] 备份当前版本...${NC}"
mkdir -p $BACKUP_DIR
if [ -d "$APP_DIR" ] && [ "$(ls -A "$APP_DIR")" ]; then
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp -r "$APP_DIR" "$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"
    echo -e "${GREEN}已备份到: $BACKUP_DIR/backup_$BACKUP_TIMESTAMP${NC}"
else
    echo -e "${YELLOW}当前版本不存在，跳过备份${NC}"
fi

# 5. 部署静态文件
echo -e "${GREEN}[5/5] 部署静态文件...${NC}"
mkdir -p "$APP_DIR"
rm -rf "$APP_DIR"/*
cp -r "$DIST_DIR"/* "$APP_DIR/"
echo -e "${GREEN}已部署到: $APP_DIR${NC}"

# 配置Nginx（首次部署时创建）
if [ ! -f "$NGINX_CONF" ]; then
    echo -e "${YELLOW}创建Nginx配置文件...${NC}"
    cat > "$NGINX_CONF" << EOF
server {
    listen 80;
    server_name _;

    root $APP_DIR;
    index index.html;

    # 前端路由支持
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API代理到后端
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 文件上传接口
    location /uploads/ {
        proxy_pass http://localhost:5000/uploads/;
        proxy_set_header Host \$host;
    }

    # 静态资源缓存
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF
    # 检查配置语法
    nginx -t
else
    echo -e "${GREEN}Nginx配置已存在，跳过创建${NC}"
fi

# 重启Nginx
echo -e "${GREEN}重启Nginx服务...${NC}"
systemctl reload nginx

echo -e ""
echo -e "${YELLOW}==============================================${NC}"
echo -e "${GREEN}✅ 前端部署完成！${NC}"
echo -e "${YELLOW}==============================================${NC}"
echo -e "${GREEN}部署目录: $APP_DIR${NC}"
echo -e "${GREEN}Git仓库: $GIT_REPO_DIR${NC}"
echo -e "${GREEN}备份目录: $BACKUP_DIR${NC}"
echo -e ""
echo -e "${YELLOW}部署模式: 静态文件直接部署${NC}"
echo -e "${YELLOW}无需Node.js，无需编译${NC}"
