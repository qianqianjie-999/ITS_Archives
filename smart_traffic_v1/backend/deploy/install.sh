#!/bin/bash
# ==============================================
# 智能交通档案系统 - 后端部署脚本
# 适用环境: Rocky Linux 9.6
# ==============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}智能交通档案系统 - 后端部署脚本${NC}"
echo -e "${YELLOW}==============================================${NC}"

# 检查是否以root用户运行
if [ "$(id -u)" != "0" ]; then
    echo -e "${RED}错误: 请以root用户运行此脚本${NC}"
    exit 1
fi

# 配置参数
DB_PASSWORD="smart_traffic_2024"
APP_DIR="/opt/smart_traffic"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="smart-traffic-backend"

echo -e "${GREEN}1. 安装系统依赖${NC}"
dnf install -y python39 python39-devel python39-pip mariadb-server mariadb-devel gcc nginx

echo -e "${GREEN}2. 启动MariaDB服务${NC}"
systemctl enable --now mariadb

echo -e "${GREEN}3. 配置数据库${NC}"
# 修改数据库初始化脚本中的密码
sed -i "s/your_password/$DB_PASSWORD/g" db_init.sql

# 执行数据库初始化脚本
mysql -u root < db_init.sql

echo -e "${GREEN}4. 创建应用目录${NC}"
mkdir -p $APP_DIR

echo -e "${GREEN}5. 创建Python虚拟环境${NC}"
python3.9 -m venv $VENV_DIR

echo -e "${GREEN}6. 安装Python依赖${NC}"
$VENV_DIR/bin/pip install --upgrade pip
$VENV_DIR/bin/pip install flask flask-restx flask-sqlalchemy flask-jwt-extended flask-cors pymysql python-dotenv bcrypt

echo -e "${GREEN}7. 创建环境配置文件${NC}"
cat > $APP_DIR/.env << EOF
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
DB_HOST=localhost
DB_PORT=3306
DB_USER=smart_traffic
DB_PASSWORD=$DB_PASSWORD
DB_NAME=smart_traffic
UPLOAD_FOLDER=$APP_DIR/uploads
EOF

echo -e "${GREEN}8. 创建上传目录${NC}"
mkdir -p $APP_DIR/uploads

echo -e "${GREEN}9. 创建systemd服务文件${NC}"
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Smart Traffic Archive System Backend
After=network.target mariadb.service

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}10. 配置Nginx反向代理${NC}"
cat > /etc/nginx/conf.d/smart-traffic.conf << EOF
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /uploads {
        alias $APP_DIR/uploads;
        expires 30d;
    }
}
EOF

echo -e "${GREEN}11. 启动服务${NC}"
systemctl daemon-reload
systemctl enable --now $SERVICE_NAME
systemctl restart nginx

echo -e "${YELLOW}==============================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${YELLOW}==============================================${NC}"
echo ""
echo -e "初始用户信息:"
echo -e "  管理员: ${YELLOW}admin${NC} / ${YELLOW}admin123${NC}"
echo -e "  编辑用户: ${YELLOW}editor${NC} / ${YELLOW}admin123${NC}"
echo -e "  查看用户: ${YELLOW}viewer${NC} / ${YELLOW}admin123${NC}"
echo ""
echo -e "注意事项:"
echo -e "  1. 请修改 $APP_DIR/.env 中的 SECRET_KEY 和 JWT_SECRET_KEY"
echo -e "  2. 请配置防火墙开放80端口"
echo -e "  3. 生产环境建议配置HTTPS"