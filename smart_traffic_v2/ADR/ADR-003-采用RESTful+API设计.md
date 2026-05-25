# ADR-003: 采用 RESTful API 设计

## 状态
已接受

## 背景
原系统使用 Flask 模板渲染，URL 设计与业务逻辑紧耦合。新架构需要前后端分离，需要一套规范的 API 设计。

## 决策
采用 RESTful API 设计风格，使用 Flask-RESTX 实现。

### API 规范

| 资源 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 认证 | `/api/auth/login` | POST | 用户登录 |
| 认证 | `/api/auth/logout` | POST | 用户登出 |
| 认证 | `/api/auth/current_user` | GET | 获取当前用户 |
| 路口 | `/api/intersections/` | GET | 列表 |
| 路口 | `/api/intersections/<id>` | GET | 详情 |
| 路口 | `/api/intersections/<id>/traffic-light/<tl_id>` | PUT | 更新信号灯 |
| 路口 | `/api/intersections/<id>/electronic-police/<ep_id>` | PUT | 更新电子警察 |
| 路口 | `/api/intersections/<id>/extend-warranty` | POST | 续保 |
| 点位 | `/api/points/` | GET | 列表 |
| 点位 | `/api/points/<id>` | GET | 详情 |
| 项目 | `/api/projects/` | GET/POST | 列表/创建 |
| 项目 | `/api/projects/<id>` | GET/PUT/DELETE | 详情/更新/删除 |
| 附件 | `/api/attachments/` | POST | 上传 |
| 附件 | `/api/attachments/<entity>/<id>` | GET | 列表 |
| 附件 | `/api/attachments/<id>` | DELETE | 删除 |
| 日志 | `/api/logs/` | GET | 列表（分页） |

### 响应格式

```json
// 成功
{
  "status": "success",
  "data": { ... }
}

// 列表（分页）
{
  "status": "success",
  "logs": [...],
  "total": 100,
  "page": 1,
  "per_page": 20
}

// 错误
{
  "status": "error",
  "message": "错误描述"
}
```

### 认证方式
使用 JWT Bearer Token，通过 `Authorization: Bearer <token>` 头部传递。

## 替代方案考虑

| 替代方案 | 优点 | 缺点 |
|---------|------|------|
| GraphQL | 灵活查询 | 复杂度高 |
| gRPC | 高性能 | 学习成本，二进制协议 |
| WebSocket | 实时双向 | 过度设计 |

## 后果

### 正面
- 前后端完全解耦
- API 可复用，支持多客户端
- Swagger 自动文档
- 标准化错误处理

### 负面
- 需处理跨域（CORS）
- 需处理文件上传（大文件）
- 实时性场景需轮询或 WebSocket