# 智能交通建设档案系统 - API接口文档

**基础URL**: `http://localhost:5000/api`
**Swagger文档**: `http://localhost:5000/api/docs`

---

## 1. API设计规范

### 1.1 RESTful设计原则

- 使用标准HTTP方法（GET, POST, PUT, DELETE）
- 资源命名使用复数名词
- 使用URL路径传递资源ID
- 使用HTTP状态码表示结果

### 1.2 认证方式

所有需要认证的API通过JWT Token验证：

```
Authorization: Bearer <token>
```

**Token获取**: 通过 `/auth/login` 接口获取

### 1.3 请求格式

**Headers**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**查询参数**: URL查询字符串

**请求体**: JSON格式

### 1.4 响应格式

**成功响应**:
```json
{
  "status": "success",
  "data": { ... }
}
```

**列表响应（分页）**:
```json
{
  "status": "success",
  "logs": [...],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

**错误响应**:
```json
{
  "status": "error",
  "message": "错误描述"
}
```

### 1.5 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 1.6 角色权限

| 角色 | 权限 |
|------|------|
| admin | 所有权限 |
| editor | 创建、更新权限 |
| viewer | 只读权限 |

---

## 2. 认证模块 API

### 2.1 用户登录

**端点**: `POST /auth/login`

**请求体**:
```json
{
  "username": "admin",
  "password": "123456"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "display_name": "管理员",
    "role": "admin",
    "is_active": true,
    "last_login": "2026-05-30T10:00:00"
  }
}
```

**错误响应** (401):
```json
{
  "status": "error",
  "message": "用户名或密码错误"
}
```

---

### 2.2 用户登出

**端点**: `POST /auth/logout`

**需要认证**: ✅

**成功响应** (200):
```json
{
  "status": "success"
}
```

---

### 2.3 获取当前用户

**端点**: `GET /auth/current_user`

**需要认证**: ✅

**成功响应** (200):
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "username": "admin",
    "display_name": "管理员",
    "role": "admin",
    "is_active": true,
    "last_login": "2026-05-30T10:00:00"
  }
}
```

---

## 3. 路口管理 API

### 3.1 获取路口列表

**端点**: `GET /intersections/`

**需要认证**: ❌

**成功响应** (200):
```json
[
  {
    "id": 1,
    "name": "人民路-解放路十字路口",
    "type": "十字路口",
    "east_west_road": "人民路",
    "north_south_road": "解放路",
    "traffic_light_warranty_status": "在保",
    "traffic_light_warranty_expire": "2027-05-30",
    "electronic_police_warranty_status": "在保",
    "electronic_police_warranty_expire": "2027-05-30"
  }
]
```

---

### 3.2 创建路口

**端点**: `POST /intersections/`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "name": "人民路-解放路十字路口",
  "type": "十字路口",
  "east_west_road": "人民路",
  "north_south_road": "解放路"
}
```

**成功响应** (201):
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "人民路-解放路十字路口",
    "type": "十字路口",
    "east_west_road": "人民路",
    "north_south_road": "解放路"
  }
}
```

---

### 3.3 获取路口详情

**端点**: `GET /intersections/{intersection_id}`

**需要认证**: ❌

**成功响应** (200):
```json
{
  "intersection": {
    "id": 1,
    "name": "人民路-解放路十字路口",
    "type": "十字路口",
    "east_west_road": "人民路",
    "north_south_road": "解放路",
    "traffic_light_warranty_status": "在保",
    "traffic_light_warranty_expire": "2027-05-30",
    "electronic_police_warranty_status": "在保",
    "electronic_police_warranty_expire": "2027-05-30"
  },
  "traffic_lights": [...],
  "electronic_polices": [...]
}
```

---

### 3.4 更新路口

**端点**: `PUT /intersections/{intersection_id}`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "name": "新路口名称",
  "type": "丁字路口"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "新路口名称",
    "type": "丁字路口"
  }
}
```

---

### 3.5 删除路口

**端点**: `DELETE /intersections/{intersection_id}`

**需要认证**: ✅ (admin)

**成功响应** (200):
```json
{
  "status": "success",
  "message": "删除成功"
}
```

---

### 3.6 创建信号灯

**端点**: `POST /intersections/{intersection_id}/traffic-light`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "project_id": 1,
  "signal_type": "智能信号机",
  "signal_count": 1,
  "left_arrow_count": 2,
  "straight_arrow_count": 3,
  "right_arrow_count": 2,
  "full_screen_count": 1,
  "non_motor_count": 2,
  "pedestrian_count": 4,
  "radar_count": 0,
  "guide_screen_count": 1,
  "power_source": "路灯电源"
}
```

**成功响应** (201):
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "intersection_id": 1,
    "project_id": 1,
    "signal_type": "智能信号机"
  }
}
```

---

### 3.7 更新信号灯

**端点**: `PUT /intersections/{intersection_id}/traffic-light/{tl_id}`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "signal_count": 2,
  "power_source": "专用电源"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 3.8 删除信号灯

**端点**: `DELETE /intersections/{intersection_id}/traffic-light/{tl_id}`

**需要认证**: ✅ (admin)

**成功响应** (200):
```json
{
  "status": "success",
  "message": "删除成功"
}
```

---

### 3.9 创建电子警察

**端点**: `POST /intersections/{intersection_id}/electronic-police`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "project_id": 1,
  "capture_type": "卡口抓拍",
  "terminal_server_count": 1,
  "forward_capture_count": 2,
  "reverse_capture_count": 2,
  "led_light_count": 4,
  "strobe_light_count": 2,
  "ptz_count": 1,
  "signal_detector_count": 1,
  "network_source": "光纤网络"
}
```

**成功响应** (201):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 3.10 更新电子警察

**端点**: `PUT /intersections/{intersection_id}/electronic-police/{ep_id}`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "capture_type": "综合抓拍",
  "forward_capture_count": 3
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 3.11 删除电子警察

**端点**: `DELETE /intersections/{intersection_id}/electronic-police/{ep_id}`

**需要认证**: ✅ (admin)

**成功响应** (200):
```json
{
  "status": "success",
  "message": "删除成功"
}
```

---

### 3.12 路口质保延期

**端点**: `POST /intersections/{intersection_id}/extend-warranty`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "device_type": "both",
  "project_id": 1,
  "warranty_expire_date": "2029-05-30"
}
```

**device_type可选值**:
- `traffic_light`: 仅信号灯
- `electronic_police`: 仅电子警察
- `both`: 所有设备

**成功响应** (200):
```json
{
  "status": "success",
  "project_id": 1,
  "message": "已为5个设备申请质保延期"
}
```

---

## 4. 点位管理 API

### 4.1 获取违停点位列表

**端点**: `GET /points/parking-points`

**需要认证**: ❌

**成功响应** (200):
```json
[
  {
    "id": 1,
    "name": "商业街违停抓拍点",
    "area": "商业街",
    "type": "违停球",
    "status": "在保",
    "latest_expire_date": "2027-05-30"
  }
]
```

---

### 4.2 创建违停点位

**端点**: `POST /points/parking-points`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "name": "商业街违停抓拍点",
  "area": "商业街",
  "type": "违停球"
}
```

**成功响应** (201):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.3 获取违停点位详情

**端点**: `GET /points/parking-points/{point_id}`

**需要认证**: ❌

**成功响应** (200):
```json
{
  "point": {...},
  "parking_enforcements": [...],
  "warranty_extensions": [...]
}
```

---

### 4.4 更新违停点位

**端点**: `PUT /points/parking-points/{point_id}`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "name": "新名称",
  "area": "新区域"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.5 删除违停点位

**端点**: `DELETE /points/parking-points/{point_id}`

**需要认证**: ✅ (admin)

**成功响应** (200):
```json
{
  "status": "success",
  "message": "删除成功"
}
```

---

### 4.6 创建违停设备

**端点**: `POST /points/parking-points/{point_id}/devices`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "project_id": 1,
  "camera_area": "商业街入口",
  "camera_count": 1,
  "parking_sign_count": 2,
  "monitor_sign_count": 1,
  "power_source": "路灯电源",
  "network_source": "光纤"
}
```

**成功响应** (201):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.7 更新违停设备

**端点**: `PUT /points/parking-points/{point_id}/devices/{pe_id}`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "camera_count": 2
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.8 删除违停设备

**端点**: `DELETE /points/parking-points/{point_id}/devices/{pe_id}`

**需要认证**: ✅ (admin)

**成功响应** (200):
```json
{
  "status": "success",
  "message": "删除成功"
}
```

---

### 4.9 违停点位质保延期

**端点**: `POST /points/parking-points/{point_id}/extend-warranty`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "project_id": 1,
  "warranty_expire_date": "2029-05-30"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.10 获取卡口点位列表

**端点**: `GET /points/checkpoint-points`

**需要认证**: ❌

**成功响应** (200):
```json
[
  {
    "id": 1,
    "name": "城区北卡口",
    "area": "城区",
    "type": "标准卡口",
    "status": "在保",
    "latest_expire_date": "2027-05-30"
  }
]
```

---

### 4.11 创建卡口点位

**端点**: `POST /points/checkpoint-points`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "name": "城区北卡口",
  "area": "城区",
  "type": "标准卡口"
}
```

**成功响应** (201):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.12 获取卡口点位详情

**端点**: `GET /points/checkpoint-points/{point_id}`

**需要认证**: ❌

**成功响应** (200):
```json
{
  "point": {...},
  "checkpoints": [...],
  "warranty_extensions": [...]
}
```

---

### 4.13 更新卡口点位

**端点**: `PUT /points/checkpoint-points/{point_id}`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "name": "新名称"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.14 删除卡口点位

**端点**: `DELETE /points/checkpoint-points/{point_id}`

**需要认证**: ✅ (admin)

**成功响应** (200):
```json
{
  "status": "success",
  "message": "删除成功"
}
```

---

### 4.15 创建卡口设备

**端点**: `POST /points/checkpoint-points/{point_id}/devices`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "project_id": 1,
  "checkpoint_type": "标准卡口",
  "camera_count": 4,
  "strobe_light_count": 4,
  "radar_count": 1,
  "sign_count": 2,
  "power_source": "专用电源",
  "network_source": "光纤"
}
```

**成功响应** (201):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.16 更新卡口设备

**端点**: `PUT /points/checkpoint-points/{point_id}/devices/{cp_id}`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "camera_count": 6
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.17 删除卡口设备

**端点**: `DELETE /points/checkpoint-points/{point_id}/devices/{cp_id}`

**需要认证**: ✅ (admin)

**成功响应** (200):
```json
{
  "status": "success",
  "message": "删除成功"
}
```

---

### 4.18 卡口点位质保延期

**端点**: `POST /points/checkpoint-points/{point_id}/extend-warranty`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "project_id": 1,
  "warranty_expire_date": "2029-05-30"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.19 获取后端设备列表

**端点**: `GET /points/backend-devices`

**需要认证**: ❌

**成功响应** (200):
```json
[
  {
    "id": 1,
    "point_id": 1,
    "project_id": 1,
    "name": "核心交换机",
    "type": "交换机",
    "server_count": 0,
    "storage_count": 0,
    "switch_count": 1
  }
]
```

---

### 4.20 创建后端设备

**端点**: `POST /points/backend-devices`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "point_id": 1,
  "project_id": 1,
  "name": "核心交换机",
  "type": "交换机",
  "server_count": 0,
  "storage_count": 0,
  "switch_count": 1,
  "firewall_count": 1,
  "ip_address": "192.168.1.1",
  "port": "8080"
}
```

**成功响应** (201):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.21 更新后端设备

**端点**: `PUT /points/backend-device/{bd_id}`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "switch_count": 2,
  "ip_address": "192.168.1.2"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 4.22 删除后端设备

**端点**: `DELETE /points/backend-device/{bd_id}`

**需要认证**: ✅ (admin)

**成功响应** (200):
```json
{
  "status": "success",
  "message": "删除成功"
}
```

---

## 5. 项目管理 API

### 5.1 获取项目列表

**端点**: `GET /projects/`

**需要认证**: ❌

**查询参数**:
- `facility_type`: 设施类型（如 `intersection`, `point`）
- `facility_id`: 设施ID

**示例**: `GET /projects/?facility_type=intersection&facility_id=1`

**成功响应** (200):
```json
[
  {
    "id": 1,
    "name": "2025年智能交通一期",
    "contract_amount": 5000000.00,
    "acceptance_date": "2025-05-30",
    "warranty_period": "2年",
    "warranty_expire_date": "2027-05-30",
    "builder": "交通管理局",
    "construction_unit": "科技有限公司"
  }
]
```

---

### 5.2 创建项目

**端点**: `POST /projects/`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "name": "2025年智能交通一期",
  "contract_amount": 5000000.00,
  "acceptance_date": "2025-05-30",
  "warranty_period": "2年",
  "warranty_expire_date": "2027-05-30",
  "builder": "交通管理局",
  "construction_unit": "科技有限公司"
}
```

**成功响应** (201):
```json
{
  "status": "success",
  "id": 1
}
```

---

### 5.3 获取项目详情

**端点**: `GET /projects/{project_id}`

**需要认证**: ❌

**成功响应** (200):
```json
{
  "id": 1,
  "name": "2025年智能交通一期",
  "contract_amount": 5000000.00,
  "acceptance_date": "2025-05-30",
  "warranty_period": "2年",
  "warranty_expire_date": "2027-05-30",
  "builder": "交通管理局",
  "construction_unit": "科技有限公司"
}
```

---

### 5.4 更新项目

**端点**: `PUT /projects/{project_id}`

**需要认证**: ✅ (admin, editor)

**请求体**:
```json
{
  "warranty_period": "3年",
  "warranty_expire_date": "2028-05-30"
}
```

**成功响应** (200):
```json
{
  "status": "success",
  "data": {...}
}
```

---

### 5.5 删除项目

**端点**: `DELETE /projects/{project_id}`

**需要认证**: ✅ (admin)

**成功响应** (200):
```json
{
  "status": "success"
}
```

---

## 6. 附件管理 API

### 6.1 获取附件列表

**端点**: `GET /attachments/`

**需要认证**: ❌

**查询参数**:
- `related_entity_type`: 实体类型
- `related_entity_id`: 实体ID

**示例**: `GET /attachments/?related_entity_type=intersection&related_entity_id=1`

**成功响应** (200):
```json
[
  {
    "id": 1,
    "related_entity_type": "intersection",
    "related_entity_id": 1,
    "file_name": "intersection_1_现场照片.jpg",
    "file_size": 1024000,
    "upload_time": "2026-05-30T10:00:00"
  }
]
```

---

### 6.2 上传附件

**端点**: `POST /attachments/upload`

**需要认证**: ✅ (admin, editor)

**Content-Type**: `multipart/form-data`

**表单字段**:
- `file`: 文件（必填）
- `related_entity_type`: 实体类型（必填）
- `related_entity_id`: 实体ID（必填）

**允许的文件类型**: pdf, doc, docx, xls, xlsx, jpg, jpeg, png, gif

**成功响应** (201):
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "file_name": "现场照片.jpg"
  }
}
```

---

### 6.3 下载附件

**端点**: `GET /attachments/{attachment_id}`

**需要认证**: ❌

**成功响应**: 文件下载

---

### 6.4 删除附件

**端点**: `DELETE /attachments/{attachment_id}`

**需要认证**: ✅ (admin)

**成功响应** (200):
```json
{
  "status": "success",
  "message": "删除成功"
}
```

---

## 7. 日志 API

### 7.1 获取操作日志

**端点**: `GET /logs/`

**需要认证**: ❌

**查询参数**:
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）

**示例**: `GET /logs/?page=1&per_page=20`

**成功响应** (200):
```json
{
  "status": "success",
  "logs": [
    {
      "id": 1,
      "user_id": 1,
      "username": "admin",
      "operation_type": "更新",
      "entity_type": "intersection",
      "entity_id": 1,
      "old_value": {...},
      "new_value": {...},
      "ip_address": "192.168.1.1",
      "operation_time": "2026-05-30T10:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

---

## 8. 导入导出 API

### 8.1 导出统计数据

**端点**: `GET /export/statistics`

**需要认证**: ❌

**成功响应**: Excel文件下载

---

### 8.2 下载导入模板

**端点**: `GET /export/template`

**需要认证**: ❌

**成功响应**: Excel模板文件下载

---

### 8.3 Excel数据导入

**端点**: `POST /import/excel`

**需要认证**: ✅ (admin, editor)

**Content-Type**: `multipart/form-data`

**表单字段**:
- `type`: 导入类型（必填）
  - `intersection`: 路口数据
  - `point`: 点位数据
  - `project`: 项目数据
  - `device`: 设备数据
- `file`: Excel文件（必填）

**成功响应** (200):
```json
{
  "status": "success",
  "message": "成功导入 10 条数据",
  "count": 10,
  "errors": []
}
```

**错误响应** (400):
```json
{
  "status": "error",
  "message": "文件格式错误",
  "errors": ["第3行数据格式错误"]
}
```

---

## 9. API访问示例

### 9.1 cURL示例

**登录并获取Token**:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456"}'
```

**获取路口列表（无需认证）**:
```bash
curl -X GET http://localhost:5000/api/intersections/
```

**创建路口（需要认证）**:
```bash
curl -X POST http://localhost:5000/api/intersections/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"name": "新路口", "type": "十字路口"}'
```

**上传附件**:
```bash
curl -X POST http://localhost:5000/api/attachments/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/file.pdf" \
  -F "related_entity_type=intersection" \
  -F "related_entity_id=1"
```

### 9.2 JavaScript示例

**登录并获取Token**:
```javascript
const response = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: '123456' })
});
const data = await response.json();
const token = data.token;
```

**创建路口**:
```javascript
const response = await fetch('http://localhost:5000/api/intersections/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ name: '新路口', type: '十字路口' })
});
const data = await response.json();
console.log(data);
```

---

## 10. 常见问题

### 10.1 如何获取JWT Token？

通过 `/auth/login` 接口，传入用户名和密码即可获取Token。

### 10.2 Token过期时间？

默认过期时间为24小时（可在配置中修改）。

### 10.3 上传文件大小限制？

默认最大上传文件大小为16MB。

### 10.4 如何处理CORS跨域？

后端已配置Flask-CORS，支持跨域请求。
