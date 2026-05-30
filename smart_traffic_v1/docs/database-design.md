# 智能交通建设档案系统 - 数据库设计文档

## 1. 数据库概述

### 1.1 数据库选型

| 项目 | 说明 |
|------|------|
| 数据库类型 | MariaDB 10.x / MySQL 8.0 |
| 字符集 | utf8mb4 |
| 排序规则 | utf8mb4_unicode_ci |
| ORM框架 | SQLAlchemy 3.x |

### 1.2 设计原则

- 每个设备表都关联 `project_id`，保留项目信息
- 路口和点位作为独立实体，设备表通过外键引用
- 续保（无新增设备）单独使用 `warranty_extension` 表记录
- 使用计算属性实时获取质保状态
- 附件表统一存储各类电子档案

---

## 2. 完整表结构定义

### 2.1 项目表 (project)

存储所有项目的通用信息，是设备质保计算的核心参考表。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 项目ID |
| name | VARCHAR(100) | NOT NULL, UNIQUE | 项目名称 |
| contract_amount | DECIMAL(15,2) | NULL | 合同金额 |
| acceptance_date | DATE | NULL | 验收日期 |
| warranty_period | VARCHAR(50) | NULL | 质保期（如"2年"） |
| warranty_expire_date | DATE | NOT NULL | 质保到期时间 |
| builder | VARCHAR(100) | NULL | 建设单位 |
| construction_unit | VARCHAR(100) | NULL | 施工单位 |

**索引：**
- PRIMARY KEY (id)
- UNIQUE (name)

**关系：**
- 一对多：project → traffic_light
- 一对多：project → electronic_police
- 一对多：project → parking_enforcement
- 一对多：project → checkpoint
- 一对多：project → backend_device
- 一对多：project → warranty_extension

---

### 2.2 路口表 (intersection)

路口基础信息，用于信号灯和电子警察设备。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 路口ID |
| name | VARCHAR(100) | NOT NULL, UNIQUE | 路口名称 |
| type | ENUM | NULL | 路口类型 |
| east_west_road | VARCHAR(100) | NULL | 东西走向道路 |
| north_south_road | VARCHAR(100) | NULL | 南北走向道路 |

**type枚举值：**
- 十字路口
- 丁字路口
- 行人过街
- 其他

**索引：**
- PRIMARY KEY (id)
- UNIQUE (name)

**关系：**
- 一对多：intersection → traffic_light
- 一对多：intersection → electronic_police

---

### 2.3 信号灯表 (traffic_light)

记录路口信号灯设备的配置信息。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | - | 信号灯ID |
| intersection_id | INT | FOREIGN KEY, NOT NULL | - | 路口ID |
| project_id | INT | FOREIGN KEY, NOT NULL | - | 所属项目ID |
| signal_type | VARCHAR(50) | NULL | - | 信号机类型（智能/非智能） |
| signal_count | INT | - | 0 | 信号机数量 |
| left_arrow_count | INT | - | 0 | 左转箭头灯数量 |
| straight_arrow_count | INT | - | 0 | 直行箭头灯数量 |
| right_arrow_count | INT | - | 0 | 右转箭头灯数量 |
| full_screen_count | INT | - | 0 | 满屏灯数量 |
| non_motor_count | INT | - | 0 | 非机动车灯数量 |
| pedestrian_count | INT | - | 0 | 行人灯数量 |
| radar_count | INT | - | 0 | 雷达数量 |
| guide_screen_count | INT | - | 0 | 诱导屏数量 |
| power_source | TEXT | NULL | - | 取电说明 |
| extended_warranty_expire_date | DATE | NULL | - | 延期质保到期时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (intersection_id) → intersection(id)
- FOREIGN KEY (project_id) → project(id)

**关系：**
- 多对一：traffic_light → intersection
- 多对一：traffic_light → project

**业务逻辑：**
- 有效质保到期时间 = extended_warranty_expire_date（若存在） OR project.warranty_expire_date
- 质保状态：根据有效质保到期时间与当前日期比较判断

---

### 2.4 电子警察表 (electronic_police)

记录路口电子警察设备配置。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | - | 电子警察ID |
| intersection_id | INT | FOREIGN KEY, NOT NULL | - | 路口ID |
| project_id | INT | FOREIGN KEY, NOT NULL | - | 所属项目ID |
| capture_type | VARCHAR(50) | NULL | - | 抓拍类型 |
| terminal_server_count | INT | - | 0 | 终端服务器数量 |
| forward_capture_count | INT | - | 0 | 前拍相机数量 |
| reverse_capture_count | INT | - | 0 | 后拍相机数量 |
| led_light_count | INT | - | 0 | LED补光灯数量 |
| strobe_light_count | INT | - | 0 | 频闪灯数量 |
| ptz_count | INT | - | 0 | 云台摄像机数量 |
| signal_detector_count | INT | - | 0 | 信号检测器数量 |
| network_source | TEXT | NULL | - | 网络取电说明 |
| extended_warranty_expire_date | DATE | NULL | - | 延期质保到期时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (intersection_id) → intersection(id)
- FOREIGN KEY (project_id) → project(id)

**关系：**
- 多对一：electronic_police → intersection
- 多对一：electronic_police → project

---

### 2.5 违停点位表 (parking_enforcement_point)

违停设备点位基础信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 违停点位ID |
| name | VARCHAR(100) | NOT NULL, UNIQUE | 点位名称 |
| area | VARCHAR(100) | NULL | 抓拍区域 |
| type | VARCHAR(50) | NULL | 设备类型 |

**索引：**
- PRIMARY KEY (id)
- UNIQUE (name)

**关系：**
- 一对多：parking_enforcement_point → parking_enforcement

---

### 2.6 违停设备表 (parking_enforcement)

记录违停抓拍设备配置。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | - | 违停设备ID |
| point_id | INT | FOREIGN KEY, NOT NULL | - | 点位ID |
| project_id | INT | FOREIGN KEY, NOT NULL | - | 所属项目ID |
| camera_area | VARCHAR(200) | NULL | - | 相机抓拍区域 |
| camera_count | INT | - | 0 | 相机数量 |
| parking_sign_count | INT | - | 0 | 违停标志数量 |
| monitor_sign_count | INT | - | 0 | 监控标志数量 |
| power_source | TEXT | NULL | - | 取电说明 |
| network_source | TEXT | NULL | - | 网络取电说明 |
| extended_warranty_expire_date | DATE | NULL | - | 延期质保到期时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (point_id) → parking_enforcement_point(id)
- FOREIGN KEY (project_id) → project(id)

**关系：**
- 多对一：parking_enforcement → parking_enforcement_point
- 多对一：parking_enforcement → project

---

### 2.7 卡口点位表 (checkpoint_point)

卡口设备点位基础信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 卡口点位ID |
| name | VARCHAR(100) | NOT NULL, UNIQUE | 点位名称 |
| area | VARCHAR(100) | NULL | 抓拍区域 |
| type | VARCHAR(50) | NULL | 设备类型 |

**索引：**
- PRIMARY KEY (id)
- UNIQUE (name)

**关系：**
- 一对多：checkpoint_point → checkpoint

---

### 2.8 卡口设备表 (checkpoint)

记录卡口设备配置。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | - | 卡口设备ID |
| point_id | INT | FOREIGN KEY, NOT NULL | - | 点位ID |
| project_id | INT | FOREIGN KEY, NOT NULL | - | 所属项目ID |
| checkpoint_type | VARCHAR(50) | NULL | - | 卡口类型 |
| camera_count | INT | - | 0 | 相机数量 |
| strobe_light_count | INT | - | 0 | 频闪灯数量 |
| radar_count | INT | - | 0 | 雷达数量 |
| sign_count | INT | - | 0 | 标志牌数量 |
| power_source | TEXT | NULL | - | 取电说明 |
| network_source | TEXT | NULL | - | 网络取电说明 |
| extended_warranty_expire_date | DATE | NULL | - | 延期质保到期时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (point_id) → checkpoint_point(id)
- FOREIGN KEY (project_id) → project(id)

**关系：**
- 多对一：checkpoint → checkpoint_point
- 多对一：checkpoint → project

---

### 2.9 后端设备表 (backend_device)

记录后端存储、服务器等设备配置。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | - | 后端设备ID |
| point_id | INT | NULL | - | 关联点位ID |
| project_id | INT | FOREIGN KEY, NOT NULL | - | 所属项目ID |
| name | VARCHAR(100) | NOT NULL, UNIQUE | - | 设备名称 |
| type | VARCHAR(50) | NULL | - | 设备类型 |
| server_count | INT | - | 0 | 服务器数量 |
| storage_count | INT | - | 0 | 存储设备数量 |
| switch_count | INT | - | 0 | 交换机数量 |
| firewall_count | INT | - | 0 | 防火墙数量 |
| fiber_converter_count | INT | - | 0 | 光纤收发器数量 |
| power_supply_count | INT | - | 0 | 电源数量 |
| cabinet_count | INT | - | 0 | 机柜数量 |
| other_device_count | INT | - | 0 | 其他设备数量 |
| ip_address | VARCHAR(100) | NULL | - | IP地址 |
| port | VARCHAR(50) | NULL | - | 端口 |
| location | VARCHAR(200) | NULL | - | 安装位置 |
| power_source | TEXT | NULL | - | 取电说明 |
| network_source | TEXT | NULL | - | 网络取电说明 |
| extended_warranty_expire_date | DATE | NULL | - | 延期质保到期时间 |

**索引：**
- PRIMARY KEY (id)
- UNIQUE (name)
- FOREIGN KEY (project_id) → project(id)

**关系：**
- 多对一：backend_device → project

---

### 2.10 用户表 (user)

系统用户信息。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | - | 用户ID |
| username | VARCHAR(50) | NOT NULL, UNIQUE | - | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | - | 密码哈希（pbkdf2:sha256） |
| display_name | VARCHAR(100) | NULL | - | 显示名称 |
| role | ENUM | - | 'viewer' | 角色 |
| created_at | TIMESTAMP | - | CURRENT_TIMESTAMP | 创建时间 |
| last_login | TIMESTAMP | NULL | - | 最后登录时间 |
| is_active | BOOLEAN | - | TRUE | 是否激活 |

**role枚举值：**
- admin：管理员
- editor：编辑者
- viewer：查看者

**索引：**
- PRIMARY KEY (id)
- UNIQUE (username)

**关系：**
- 一对多：user → operation_log

**安全说明：**
- 密码使用 pbkdf2:sha256 加密存储
- 密码验证通过 werkzeug.security.check_password_hash

---

### 2.11 操作日志表 (operation_log)

记录用户操作历史。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 日志ID |
| user_id | INT | FOREIGN KEY, NULL | 用户ID |
| username | VARCHAR(50) | NULL | 用户名（冗余存储） |
| operation_type | VARCHAR(50) | NOT NULL | 操作类型 |
| entity_type | VARCHAR(50) | NULL | 实体类型 |
| entity_id | INT | NULL | 实体ID |
| old_value | TEXT | NULL | 旧值 |
| new_value | TEXT | NULL | 新值 |
| ip_address | VARCHAR(50) | NULL | IP地址 |
| operation_time | TIMESTAMP | CURRENT_TIMESTAMP | 操作时间 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (user_id) → user(id)

**关系：**
- 多对一：operation_log → user

---

### 2.12 质保延期表 (warranty_extension)

记录设备质保延期信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 延期记录ID |
| facility_type | VARCHAR(50) | NOT NULL | 设备类型 |
| facility_id | INT | NOT NULL | 设备ID |
| project_id | INT | FOREIGN KEY, NOT NULL | 项目ID |
| extension_date | DATE | NOT NULL | 延期日期 |

**索引：**
- PRIMARY KEY (id)
- FOREIGN KEY (project_id) → project(id)

**facility_type 可选值：**
- traffic_light
- electronic_police
- parking_enforcement
- checkpoint
- backend_device

**关系：**
- 多对一：warranty_extension → project

---

### 2.13 附件表 (attachment)

统一存储各类电子档案。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 附件ID |
| related_entity_type | VARCHAR(50) | NOT NULL | 关联实体类型 |
| related_entity_id | INT | NOT NULL | 关联实体ID |
| file_name | VARCHAR(255) | NOT NULL | 文件名 |
| file_path | VARCHAR(500) | NOT NULL | 文件存储路径 |
| file_size | INT | NULL | 文件大小（字节） |
| mime_type | VARCHAR(100) | NULL | MIME类型 |
| upload_time | TIMESTAMP | CURRENT_TIMESTAMP | 上传时间 |
| uploaded_by | VARCHAR(100) | NULL | 上传者 |
| description | TEXT | NULL | 文件描述 |

**索引：**
- PRIMARY KEY (id)

---

## 3. 表关系图

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│  project    │──────<│ traffic_light    │       │ intersection│
└─────────────┘       └──────────────────┘       └─────────────┘
      │                      │                       │
      │                      │                       │
      │               ┌──────────────┐               │
      │               │electronic_police            │
      │               └──────────────┘               │
      │                                              │
      │               ┌──────────────────────┐      │
      ├──────────────<│parking_enforcement   │>─────┤
      │               └──────────────────────┘      │
      │                      │                       │
      │               ┌────────────┐                 │
      ├──────────────<│checkpoint  │                 │
      │               └────────────┘                 │
      │                      │                       │
      │               ┌────────────┐                 │
      ├──────────────<│backend_device              │
      │               └────────────┘                 │
      │                                              │
      │               ┌──────────────────┐           │
      ├──────────────<│warranty_extension           │
      │               └──────────────────┘           │
      │                                              │
      │               ┌──────────────────┐           │
      └──────────────<│operation_log    │           │
                      └──────────────────┘           │
                             │                        │
                             v                        │
                      ┌────────────┐                 │
                      │   user     │                 │
                      └────────────┘                 │

┌─────────────────┐
│  attachment      │
│ (独立实体)       │
└─────────────────┘
```

---

## 4. 核心业务逻辑

### 4.1 质保状态计算规则

所有设备表都实现了统一的质保状态计算逻辑：

```python
@property
def effective_warranty_expire_date(self):
    # 优先使用延期质保到期时间
    if self.extended_warranty_expire_date:
        return self.extended_warranty_expire_date
    # 否则使用项目质保到期时间
    if self.project and self.project.warranty_expire_date:
        return self.project.warranty_expire_date
    return None

@property
def warranty_status(self) -> str:
    expire_date = self.effective_warranty_expire_date
    if expire_date:
        if expire_date >= date.today():
            return '在保'
        else:
            return '过保'
    return '无项目'
```

**判断逻辑：**
- 如果存在 `extended_warranty_expire_date`，使用延期后的时间
- 否则使用关联项目的 `warranty_expire_date`
- 当前日期 >= 质保到期日期 → 在保
- 当前日期 < 质保到期日期 → 过保
- 无关联项目 → 无项目

### 4.2 混合状态计算

对于路口和点位，一个实体可能关联多个设备，每个设备可能有不同的质保状态：

```python
def _get_device_warranty(self, devices):
    expire_dates = []
    for device in devices:
        expire_date = device.effective_warranty_expire_date
        if expire_date:
            expire_dates.append(expire_date)

    if not expire_dates:
        return {'warranty_status': '无项目', 'latest_expire_date': None}

    today = date.today()
    in_warranty = sum(1 for d in expire_dates if d >= today)
    expired = sum(1 for d in expire_dates if d < today)

    if expired == 0:
        status = '在保'
    elif in_warranty == 0:
        status = '过保'
    else:
        status = '混合'

    latest = max(expire_dates)
    return {
        'warranty_status': status,
        'latest_expire_date': latest.isoformat()
    }
```

**状态说明：**
- 在保：所有设备都在质保期内
- 过保：所有设备都已过质保期
- 混合：部分在保，部分过保

### 4.3 设备与项目关联关系

```
路口 (intersection)
  ├── 信号灯 (traffic_light) ─────────> 项目 (project)
  └── 电子警察 (electronic_police) ───> 项目 (project)

点位 (parking_enforcement_point / checkpoint_point)
  ├── 违停设备 (parking_enforcement) ──> 项目 (project)
  └── 卡口设备 (checkpoint) ──────────> 项目 (project)

后端设备 (backend_device) ─────────────> 项目 (project)
```

---

## 5. 索引设计

| 表名 | 索引类型 | 索引字段 | 说明 |
|------|----------|----------|------|
| project | PRIMARY | id | 主键 |
| project | UNIQUE | name | 项目名唯一 |
| intersection | PRIMARY | id | 主键 |
| intersection | UNIQUE | name | 路口名唯一 |
| traffic_light | PRIMARY | id | 主键 |
| traffic_light | FOREIGN KEY | intersection_id | 路口外键 |
| traffic_light | FOREIGN KEY | project_id | 项目外键 |
| electronic_police | PRIMARY | id | 主键 |
| electronic_police | FOREIGN KEY | intersection_id | 路口外键 |
| electronic_police | FOREIGN KEY | project_id | 项目外键 |
| parking_enforcement_point | PRIMARY | id | 主键 |
| parking_enforcement_point | UNIQUE | name | 点位名唯一 |
| parking_enforcement | PRIMARY | id | 主键 |
| parking_enforcement | FOREIGN KEY | point_id | 点位外键 |
| parking_enforcement | FOREIGN KEY | project_id | 项目外键 |
| checkpoint_point | PRIMARY | id | 主键 |
| checkpoint_point | UNIQUE | name | 点位名唯一 |
| checkpoint | PRIMARY | id | 主键 |
| checkpoint | FOREIGN KEY | point_id | 点位外键 |
| checkpoint | FOREIGN KEY | project_id | 项目外键 |
| backend_device | PRIMARY | id | 主键 |
| backend_device | UNIQUE | name | 设备名唯一 |
| backend_device | FOREIGN KEY | project_id | 项目外键 |
| user | PRIMARY | id | 主键 |
| user | UNIQUE | username | 用户名唯一 |
| operation_log | PRIMARY | id | 主键 |
| operation_log | FOREIGN KEY | user_id | 用户外键 |
| warranty_extension | PRIMARY | id | 主键 |
| warranty_extension | FOREIGN KEY | project_id | 项目外键 |
| attachment | PRIMARY | id | 主键 |

---

## 6. 数据迁移指南

### 6.1 初始化数据库

```bash
cd /home/qianqianjie/ITS_Archives/smart_traffic_v1/backend

# 使用 Flask-Migrate 初始化
flask db init

# 生成迁移脚本
flask db migrate -m "Initial schema"

# 执行迁移
flask db upgrade
```

### 6.2 查看迁移状态

```bash
flask db current
flask db history
```

### 6.3 回滚迁移

```bash
# 回滚上一个迁移
flask db downgrade

# 回滚到指定版本
flask db downgrade <revision>
```
