# ADR-001: 采用 Flask + SQLAlchemy 后端架构

## 状态
已接受

## 背景
原系统使用 Flask 裸用 + PyMySQL 原生 SQL，存在以下问题：
- SQL 拼接容易引发注入风险
- 缺乏数据库迁移工具，版本管理困难
- 模型层与业务逻辑耦合严重
- 配置信息分散，难以集中管理

## 决策
采用 Flask + Flask-SQLAlchemy + Flask-Migrate 技术栈构建后端。

### 核心组件

| 组件 | 用途 |
|------|------|
| Flask-SQLAlchemy 3.x | ORM 映射，自动处理 SQL 注入防护 |
| Flask-Migrate | Alembic 驱动的数据库版本管理 |
| Flask-RESTX | RESTful API 自动文档生成 + 参数校验 |
| Flask-CORS | 跨域资源共享支持 |

### 项目结构

```
backend/
├── app/
│   ├── __init__.py          # Flask 应用工厂
│   ├── config.py            # 配置管理（支持多环境）
│   ├── extensions.py        # 扩展初始化
│   ├── models/              # SQLAlchemy 模型
│   ├── api/                 # REST API 蓝图
│   ├── services/            # 业务逻辑层
│   └── utils/               # 工具函数
├── migrations/              # Alembic 迁移脚本
└── run.py                   # 应用入口
```

## 替代方案考虑

| 替代方案 | 优点 | 缺点 |
|---------|------|------|
| MySQL | 成熟稳定 | 闭源，授权费用 |
| PostgreSQL | 功能丰富，GIS 支持强 | 语法差异大 |
| SQLite | 零配置，嵌入式 | 不适合生产环境 |
| Django ORM | 功能完整 | 过度设计，学习曲线陡峭 |
| SQLAlchemy Core | 轻量 | 仍需手写 SQL |

## 后果

### 正面
- 彻底解决 SQL 注入风险
- 数据库版本可控，支持回滚
- 配置集中管理，支持多环境
- API 自动文档，降低沟通成本

### 负面
- 学习曲线：需要熟悉 ORM 概念
- 性能开销：少量性能损耗（可忽略）
- 迁移成本：从原系统迁移需测试验证