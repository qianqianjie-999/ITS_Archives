# 智能交通建设档案系统 v2.0

基于 Flask + SQLAlchemy + Vue 3 的现代化重构版本。

## 技术栈

### 后端
- **框架**: Flask 3.0 + Flask-RESTX
- **数据库**: MariaDB 10.x
- **ORM**: SQLAlchemy 3.x (解决 SQL 注入问题)
- **迁移**: Flask-Migrate (Alembic)
- **认证**: JWT (PyJWT)
- **文档**: Swagger (自动生成)

### 前端
- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **构建**: Vite 5
- **路由**: Vue Router 4
- **状态**: Pinia
- **UI**: Element Plus

## 快速开始

### 1. 克隆项目

```bash
cd smart_traffic_v2
```

### 2. 后端安装

```bash
cd backend
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env  # 编辑 .env 设置数据库连接

# 初始化数据库（使用原有数据）
# mysql -u root -p < ../../smart_traffic/init_database.sql

# 运行应用
python run.py
```

API 文档访问: http://localhost:5000/api/docs

### 3. 前端安装

```bash
cd frontend
npm install

# 运行开发服务器
npm run dev
```

访问: http://localhost:3000

## 目录结构

```
smart_traffic_v2/
├── backend/                    # Flask 后端
│   ├── app/
│   │   ├── models/            # SQLAlchemy 模型
│   │   ├── api/               # REST API 端点
│   │   ├── services/          # 业务逻辑
│   │   └── utils/             # 工具函数
│   ├── migrations/            # 数据库迁移
│   └── run.py                 # 入口
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/              # API 调用
│   │   ├── views/            # 页面组件
│   │   ├── stores/           # Pinia 状态
│   │   └── router/           # 路由配置
│   └── package.json
│
└── ADR/                       # 架构决策记录
```

## 改进点

| 问题 | 解决方案 |
|------|----------|
| SQL 注入风险 | SQLAlchemy ORM 参数化查询 |
| 配置外泄 | dotenv 环境变量管理 |
| 前端技术栈 | Vue 3 + TypeScript |
| 错误处理 | 统一错误响应格式 |
| CORS | Flask-CORS 配置 |
| 上传目录 | 绝对路径 + 环境变量 |
| API 文档 | Swagger 自动生成 |