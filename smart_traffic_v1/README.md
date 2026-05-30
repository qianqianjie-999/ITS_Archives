# 智能交通建设档案系统

基于 Flask + SQLAlchemy + Vue 3 的现代化前后端分离系统，用于管理智能交通领域设备档案。

## 项目简介

智能交通建设档案系统是一套用于管理智能交通领域前端设备（信号灯、电子警察、违停球、卡口）、后端设备、项目信息、质保状态及电子档案的综合管理平台。

### 核心功能

- **路口管理**：信号灯、电子警察设备配置与质保管理
- **点位管理**：违停抓拍设备、卡口设备配置与质保管理
- **项目管理**：项目信息、验收日期、质保期限管理
- **后端设备**：服务器、存储、网络设备管理
- **质保延期**：设备质保状态追踪与延期操作
- **附件管理**：电子档案上传、下载与关联
- **数据分析**：设备统计数据导出
- **操作日志**：用户操作行为审计追踪

### 技术栈

#### 后端

- **框架**: Flask 3.0 + Flask-RESTX
- **数据库**: MariaDB 10.x / MySQL 8.0
- **ORM**: SQLAlchemy 3.x
- **迁移**: Flask-Migrate (Alembic)
- **认证**: JWT (PyJWT)
- **文档**: Swagger (自动生成)
- **Excel**: openpyxl

#### 前端

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **构建**: Vite 5
- **路由**: Vue Router 4
- **状态**: Pinia
- **UI组件**: Element Plus
- **HTTP**: Axios

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    前端 (Vue 3)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  页面组件 │  │  API调用  │  │   状态管理(Pinia) │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└────────────────────────┬────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────┴────────────────────────────┐
│                   后端 (Flask)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ REST API │  │ Services │  │   Models (ORM)   │    │
│  └──────────┘  └──────────┘  └──────────────────┘    │
└────────────────────────┬────────────────────────────┘
                         │ SQLAlchemy
┌────────────────────────┴────────────────────────────┐
│               数据库 (MariaDB/MySQL)                  │
└─────────────────────────────────────────────────────┘
```

## 项目结构

```
smart_traffic_v1/
├── backend/                         # Flask 后端
│   ├── app/
│   │   ├── api/                    # REST API 端点
│   │   │   ├── auth.py            # 认证接口
│   │   │   ├── intersections.py   # 路口管理接口
│   │   │   ├── points.py          # 点位管理接口
│   │   │   ├── projects.py        # 项目管理接口
│   │   │   ├── attachments.py     # 附件管理接口
│   │   │   ├── logs.py            # 日志接口
│   │   │   ├── export.py          # 导出接口
│   │   │   └── import_api.py      # 导入接口
│   │   ├── models/                # SQLAlchemy 模型
│   │   │   ├── intersection.py    # 路口、信号灯、电子警察模型
│   │   │   ├── point.py           # 违停、卡口设备模型
│   │   │   ├── project.py         # 项目模型
│   │   │   ├── user.py            # 用户、日志模型
│   │   │   ├── backend_device.py  # 后端设备模型
│   │   │   ├── warranty_extension.py  # 质保延期模型
│   │   │   └── attachment.py      # 附件模型
│   │   ├── services/              # 业务逻辑层
│   │   │   ├── auth_service.py    # 认证服务
│   │   │   ├── excel_export_service.py  # Excel导出
│   │   │   ├── excel_import_service.py   # Excel导入
│   │   │   └── warranty_service.py       # 质保服务
│   │   ├── utils/                 # 工具函数
│   │   │   └── decorators.py      # 认证装饰器
│   │   ├── config.py              # 配置管理
│   │   ├── extensions.py          # Flask 扩展初始化
│   │   └── __init__.py            # 应用工厂
│   ├── migrations/                 # 数据库迁移脚本
│   ├── requirements.txt           # Python 依赖
│   └── run.py                     # 应用入口
│
├── frontend/                        # Vue 3 前端
│   ├── src/
│   │   ├── api/                   # API 调用层
│   │   │   ├── index.ts          # Axios 实例
│   │   │   ├── intersections.ts  # 路口 API
│   │   │   ├── points.ts         # 点位 API
│   │   │   ├── projects.ts       # 项目 API
│   │   │   └── attachments.ts    # 附件 API
│   │   ├── components/            # 公共组件
│   │   │   ├── AppHeader.vue     # 顶部导航
│   │   │   └── AppSidebar.vue    # 侧边菜单
│   │   ├── views/                 # 页面组件
│   │   │   ├── Login.vue         # 登录页
│   │   │   ├── Dashboard.vue     # 仪表盘
│   │   │   ├── IntersectionList.vue    # 路口列表
│   │   │   ├── IntersectionDetail.vue  # 路口详情
│   │   │   ├── ParkingEnforcementList.vue  # 违停列表
│   │   │   ├── ParkingEnforcementDetail.vue  # 违停详情
│   │   │   ├── CheckpointList.vue     # 卡口列表
│   │   │   ├── CheckpointDetail.vue    # 卡口详情
│   │   │   ├── ProjectList.vue     # 项目列表
│   │   │   ├── BackendDeviceList.vue   # 后端设备列表
│   │   │   ├── Statistics.vue      # 统计分析
│   │   │   └── Home.vue            # 首页
│   │   ├── router/                # 路由配置
│   │   │   └── index.ts
│   │   ├── stores/                # Pinia 状态
│   │   │   └── user.ts
│   │   ├── types/                 # TypeScript 类型
│   │   │   └── index.ts
│   │   ├── styles/                # 全局样式
│   │   │   ├── variables.scss
│   │   │   └── global.scss
│   │   ├── App.vue                # 根组件
│   │   └── main.ts                # 入口文件
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── ADR/                            # 架构决策记录
│   ├── ADR-001-采用Flask+SQLAlchemy后端架构.md
│   ├── ADR-002-采用Vue3+TypeScript前端架构.md
│   ├── ADR-003-采用RESTful+API设计.md
│   ├── ADR-004-JWT认证机制.md
│   ├── ADR-005-质保状态计算策略.md
│   ├── ADR-006-文件上传与存储方案.md
│   ├── ADR-007-前端路由与权限控制.md
│   └── ADR-008-数据导入导出设计.md
│
├── docs/                           # 技术文档
│   ├── database-design.md         # 数据库设计文档
│   ├── api-documentation.md       # API接口文档
│   ├── specs/                      # 设计规格
│   └── plans/                      # 实现计划
│
└── README.md                       # 项目说明文档
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+ 或 yarn
- MySQL 8.0+ 或 MariaDB 10.5+

### 1. 克隆项目

```bash
cd smart_traffic_v1
```

### 2. 后端安装

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env  # 编辑 .env 设置数据库连接

# 初始化数据库
flask db init
flask db migrate -m "Initial schema"
flask db upgrade

# 创建管理员账户
python -c "from app.models.user import User; from app.extensions import db; app = __import__('app', fromlist=['create_app']).create_app(); app.app_context().push(); u = User(username='admin', role='admin'); u.set_password('admin123'); db.session.add(u); db.session.commit()"

# 运行应用
python run.py
```

API 文档访问: http://localhost:5000/api/docs

### 3. 前端安装

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

访问: http://localhost:5173

### 4. 登录系统

默认管理员账户：
- 用户名: `admin`
- 密码: `admin123`

## 详细配置

### 环境变量配置

**后端 (.env)**

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=smart_traffic

# JWT配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=86400

# CORS配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 上传配置
UPLOAD_FOLDER=uploads
```

**前端 (.env 或 vite.config.ts)**

```bash
VITE_API_BASE_URL=http://localhost:5000/api
```

### 数据库配置

```python
# backend/app/config.py
SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)
```

### CORS 配置

后端已配置 Flask-CORS，允许以下来源：
- http://localhost:5173 (前端开发服务器)
- http://localhost:3000 (备用端口)

### 上传文件夹

默认上传目录：`backend/uploads/`

可在 `.env` 中通过 `UPLOAD_FOLDER` 配置自定义路径。

## 开发指南

### 代码规范

**后端 (Python)**

- 遵循 PEP 8 代码规范
- 使用 Type Hints 提高代码可读性
- 路由函数不超过50行，业务逻辑放入 Service 层
- 所有数据库操作通过 SQLAlchemy ORM
- 使用装饰器进行认证和权限控制

**前端 (Vue/TypeScript)**

- 遵循 Vue 3 Composition API 最佳实践
- 使用 TypeScript 严格模式
- 组件文件不超过300行
- API 调用统一封装在 `src/api/` 目录
- 使用 Pinia 进行状态管理

### 开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **编写代码**

3. **运行测试**
   ```bash
   # 后端
   pytest

   # 前端
   npm run lint
   npm run typecheck
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. **推送并创建 PR**

### 调试方法

**后端调试**

```python
# 使用 Flask 调试模式
export FLASK_DEBUG=1
python run.py

# 或使用 IDE 的调试功能
```

**前端调试**

```bash
# 启动开发服务器（支持热更新）
npm run dev

# 生产构建
npm run build

# TypeScript 类型检查
npm run typecheck

# ESLint 检查
npm run lint
```

## 部署指南

### 生产环境部署

#### 1. 后端部署

```bash
# 安装生产环境依赖
pip install gunicorn

# 使用 Gunicorn 运行
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"

# 或使用 systemd 管理进程
```

#### 2. 前端部署

```bash
# 构建生产版本
npm run build

# 构建产物在 dist/ 目录
# 可使用 Nginx 托管
```

#### 3. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/smart_traffic_v1/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4. 进程管理 (systemd)

```ini
# /etc/systemd/system/smart-traffic.service
[Unit]
Description=Smart Traffic Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/smart_traffic_v1/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app('production')"
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker 部署（可选）

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app('production')"]
```

## 数据模型

### 核心实体关系

```
项目 (Project)
├── 信号灯 (TrafficLight) ──────────> 路口 (Intersection)
├── 电子警察 (ElectronicPolice) ───> 路口 (Intersection)
├── 违停设备 (ParkingEnforcement) ─> 违停点位 (ParkingEnforcementPoint)
├── 卡口设备 (Checkpoint) ─────────> 卡口点位 (CheckpointPoint)
└── 后端设备 (BackendDevice)

路口/点位 ──> 附件 (Attachment)
用户 ──> 操作日志 (OperationLog)
```

### 质保计算逻辑

```
有效质保到期日期 =
    extended_warranty_expire_date (延期日期)
    OR project.warranty_expire_date (项目日期)

质保状态 =
    在保: 有效日期 >= 当前日期
    过保: 有效日期 < 当前日期
    无项目: 无有效日期
```

## API 文档

完整 API 文档请参考：[docs/api-documentation.md](docs/api-documentation.md)

Swagger UI 访问：http://localhost:5000/api/docs

### 主要接口

| 模块 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 认证 | /api/auth/login | POST | 用户登录 |
| 认证 | /api/auth/logout | POST | 用户登出 |
| 路口 | /api/intersections/ | GET | 路口列表 |
| 路口 | /api/intersections/{id} | GET | 路口详情 |
| 违停 | /api/points/parking-points | GET | 违停点位列表 |
| 卡口 | /api/points/checkpoint-points | GET | 卡口点位列表 |
| 项目 | /api/projects/ | GET/POST | 项目列表/创建 |
| 附件 | /api/attachments/upload | POST | 上传附件 |
| 日志 | /api/logs/ | GET | 操作日志 |
| 导入 | /api/import/excel | POST | Excel导入 |
| 导出 | /api/export/statistics | GET | 统计数据导出 |

## 常见问题

### 1. 数据库连接失败

**错误**: `Can't connect to MySQL server`

**解决方案**:
- 检查 MySQL 服务是否运行
- 确认主机名、端口、用户名、密码配置正确
- 检查防火墙是否允许 MySQL 端口

### 2. Token 过期

**错误**: `令牌已过期`

**解决方案**:
- 重新登录获取新 Token
- Token 默认24小时过期

### 3. CORS 跨域错误

**错误**: `CORS policy blocked`

**解决方案**:
- 检查后端 `CORS_ORIGINS` 环境变量配置
- 确认前端访问地址在允许列表中

### 4. 文件上传失败

**错误**: `文件类型不允许`

**解决方案**:
- 检查文件扩展名是否在允许列表中
- 确认上传目录存在且有写入权限

### 5. 数据导入格式错误

**错误**: `第X行: 数据格式错误`

**解决方案**:
- 参考导出模板的格式
- 确保必填字段不为空
- 检查日期格式是否为 YYYY-MM-DD

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试
chore: 构建/工具
```

### 开发资源

- [Flask 文档](https://flask.palletsprojects.com/)
- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

## 许可证

本项目仅供学习交流使用。

## 联系方式

如有问题，请提交 Issue 或联系开发团队。
