#!/bin/bash
# ==============================================
# 智能交通档案系统 - 前端部署脚本
# 适用环境: Rocky Linux 9.6
# ==============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}智能交通档案系统 - 前端部署脚本${NC}"
echo -e "${YELLOW}==============================================${NC}"

# 配置参数
APP_DIR="/opt/smart_traffic_frontend"
NGINX_CONF="/etc/nginx/conf.d/smart-traffic-frontend.conf"

echo -e "${GREEN}1. 安装Node.js${NC}"
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
dnf install -y nodejs

echo -e "${GREEN}2. 构建前端项目${NC}"
npm install
npm run build

echo -e "${GREEN}3. 创建部署目录${NC}"
mkdir -p $APP_DIR

echo -e "${GREEN}4. 复制构建产物${NC}"
cp -r dist/* $APP_DIR/

echo -e "${GREEN}5. 配置Nginx${NC}"
cat > $NGINX_CONF << EOF
server {
    listen 80;
    server_name frontend.localhost;

    root $APP_DIR;
    index index.html;

    # 前端路由支持
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
EOF

echo -e "${GREEN}6. 重启Nginx${NC}"
systemctl restart nginx

echo -e "${YELLOW}==============================================${NC}"
echo -e "${GREEN}前端部署完成！${NC}"
echo -e "${YELLOW}==============================================${NC}"