#!/bin/bash
# ==============================================
# 智能交通档案系统 - 后端部署脚本
# 适用环境: Rocky Linux 9.6
# 功能: GitHub拉取 → 虚拟环境 → Gunicorn启动
# ==============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置参数
APP_DIR="/opt/smart_traffic_v1"
BACKEND_DIR="$APP_DIR/backend"
VENV_DIR="$APP_DIR/venv"
GIT_REPO_DIR="/opt/smart_traffic_v1"  # Git仓库目录
SERVICE_NAME="smart-traffic-backend"
PORT=5000

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}智能交通档案系统 - 后端部署脚本${NC}"
echo -e "${YELLOW}模式: GitHub拉取 → 虚拟环境 → Gunicorn${NC}"
echo -e "${YELLOW}==============================================${NC}"

# 1. 检查Git并拉取代码
echo -e "${GREEN}[1/7] 检查Git环境并拉取最新代码...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git未安装，正在安装...${NC}"
    dnf install -y git
fi

cd $GIT_REPO_DIR
echo -e "${BLUE}当前目录: $(pwd)${NC}"
echo -e "${BLUE}Git状态:${NC}"
git status --short | head -10

echo -e "${GREEN}拉取最新代码...${NC}"
git pull origin main
echo -e "${GREEN}代码拉取完成！${NC}"

# 2. 检查/安装Python和虚拟环境
echo -e "${GREEN}[2/7] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3未安装，正在安装...${NC}"
    dnf install -y python3 python3-venv python3-pip
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}Python版本: $PYTHON_VERSION${NC}"

# 3. 创建/更新虚拟环境
echo -e "${GREEN}[3/7] 设置Python虚拟环境...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}虚拟环境已存在，更新依赖...${NC}"
else
    echo -e "${GREEN}创建新的虚拟环境...${NC}"
    python3 -m venv $VENV_DIR
fi

# 4. 安装依赖
echo -e "${GREEN}[4/7] 安装Python依赖...${NC}"
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r $BACKEND_DIR/requirements.txt
pip install gunicorn
echo -e "${GREEN}依赖安装完成！${NC}"
deactivate

# 5. 数据库初始化
echo -e "${GREEN}[5/7] 检查并初始化数据库...${NC}"
if ! systemctl is-active --quiet mariadb; then
    echo -e "${YELLOW}启动MariaDB服务...${NC}"
    systemctl enable --now mariadb
fi

# 检查.env中的数据库密码
if [ -f "$APP_DIR/.env" ]; then
    DB_PASSWORD=$(grep "^DB_PASSWORD=" "$APP_DIR/.env" | cut -d'=' -f2)
    if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "your_db_password" ]; then
        echo -e "${RED}错误: .env 中 DB_PASSWORD 未设置或仍为占位符。请先编辑 $APP_DIR/.env${NC}"
        exit 1
    fi
else
    echo -e "${RED}错误: 未找到 $APP_DIR/.env，请先创建环境配置文件。${NC}"
    exit 1
fi

# 修改db_init.sql中的密码占位符
sed -i "s/your_password/$DB_PASSWORD/g" $BACKEND_DIR/deploy/db_init.sql

# 执行数据库初始化脚本
echo -e "${GREEN}执行数据库初始化脚本...${NC}"
mysql -u root < $BACKEND_DIR/deploy/db_init.sql
echo -e "${GREEN}数据库初始化完成！${NC}"

# 6. 创建上传目录
echo -e "${GREEN}[6/7] 创建必要的目录...${NC}"
mkdir -p $APP_DIR/uploads
mkdir -p $APP_DIR/logs

# 7. 配置并启动服务
echo -e "${GREEN}[7/7] 配置并启动Gunicorn服务...${NC}"

# 检查是否有环境配置文件
if [ ! -f "$APP_DIR/.env" ]; then
    echo -e "${YELLOW}环境配置文件不存在，创建默认配置...${NC}"
    cat > $APP_DIR/.env << EOF
SECRET_KEY=change-this-secret-key-in-production
JWT_SECRET_KEY=change-this-jwt-secret-key-in-production
DB_HOST=localhost
DB_PORT=3306
DB_USER=smart_traffic
DB_PASSWORD=your_db_password
DB_NAME=smart_traffic
UPLOAD_FOLDER=$APP_DIR/uploads
PORT=$PORT
DEBUG=False
EOF
    echo -e "${YELLOW}请编辑 $APP_DIR/.env 配置数据库密码等敏感信息${NC}"
fi

# 创建systemd服务文件
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Smart Traffic Backend API
After=network.target mariadb.service

[Service]
Type=notify
User=root
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="FLASK_APP=run.py"
ExecStart=$VENV_DIR/bin/gunicorn -w 4 -b 127.0.0.1:$PORT --timeout 120 --access-logfile $APP_DIR/logs/access.log --error-logfile $APP_DIR/logs/error.log run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd配置
systemctl daemon-reload

# 启用并启动服务
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# 检查服务状态
sleep 2
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e ""
    echo -e "${YELLOW}==============================================${NC}"
    echo -e "${GREEN}✅ 后端部署成功！${NC}"
    echo -e "${YELLOW}==============================================${NC}"
    echo -e "${GREEN}服务状态: 运行中${NC}"
    echo -e "${GREEN}监听端口: $PORT${NC}"
    echo -e "${GREEN}工作目录: $BACKEND_DIR${NC}"
    echo -e "${GREEN}虚拟环境: $VENV_DIR${NC}"
    echo -e "${GREEN}日志目录: $APP_DIR/logs${NC}"
    echo -e "${GREEN}环境配置: $APP_DIR/.env${NC}"
    echo -e ""
    echo -e "${YELLOW}常用命令:${NC}"
    echo -e "  查看状态: systemctl status $SERVICE_NAME"
    echo -e "  查看日志: journalctl -u $SERVICE_NAME -f"
    echo -e "  重启服务: systemctl restart $SERVICE_NAME"
    echo -e "  停止服务: systemctl stop $SERVICE_NAME"
else
    echo -e "${RED}服务启动失败，请检查日志${NC}"
    echo -e "${YELLOW}查看错误日志:${NC}"
    journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi
