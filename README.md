# ITS_Archives · 智能交通系统档案仓库

本仓库归档智能交通领域的多个子系统项目源码与文档。

## 📦 子项目

### smart_traffic_v1 — 智能交通建设档案系统

基于 **Flask + SQLAlchemy + Vue 3** 的前后端分离系统，用于管理智能交通领域设备档案。

#### 核心功能

- **路口管理**：信号灯、电子警察设备配置与质保管理
- **点位管理**：违停抓拍设备、卡口设备配置与质保管理
- **结构化相机**：SkyNet 结构化相机点位与设备管理
- **项目管理**：项目信息、验收日期、质保期限管理
- **后端设备**：服务器、存储、网络设备管理
- **质保延期**：设备质保状态追踪与延期操作
- **维修记录**：设备故障记录与维修日志管理
- **附件管理**：电子档案上传、下载与关联
- **数据分析**：设备统计数据导出
- **操作日志**：用户操作行为审计追踪
- **用户管理**：用户账户与角色权限控制

#### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask 3.0 · Flask-RESTX · SQLAlchemy · JWT |
| 前端 | Vue 3 · TypeScript · Vite 5 · Element Plus · Pinia |
| 数据库 | MariaDB 10.x / MySQL 8.0 |
| 迁移 | Flask-Migrate (Alembic) |

#### 目录结构

```
smart_traffic_v1/
├── backend/        # Flask 后端 (API + Swagger)
├── frontend/       # Vue 3 前端
├── docs/           # 接口文档、数据库设计、操作手册
├── ADR/            # 架构决策记录 (8 篇)
└── QUICK_START.md  # 快速开始指南
```

详细说明见 [smart_traffic_v1/README.md](smart_traffic_v1/README.md)。

## 📂 仓库内容

```
ITS_Archives/
├── smart_traffic_v1/   # 智能交通建设档案系统
└── test_login.py       # 登录测试脚本
```

## 📌 相关项目

- [traffic_volume](https://github.com/qianqianjie-999/traffic_volume) — 交通流量采集与信号配时系统

## 📄 License

MIT
