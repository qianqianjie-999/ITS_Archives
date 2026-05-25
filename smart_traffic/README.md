# 智能交通建设档案系统

基于 Flask + MySQL 的智能交通建设档案管理系统，支持路口/点位管理、设备配置、质保状态查看和续保操作。

## 功能特性

- **用户登录与权限管理**：支持管理员、编辑、查看三种角色
- **路口管理**：查看所有路口及质保状态，支持续保操作
- **路口详情**：查看信号灯和电子警察设备信息，支持编辑
- **点位管理**：查看违停球和卡口点位信息
- **项目管理**：查看所有项目信息
- **附件上传**：支持为路口上传验收报告、施工图等附件
- **操作日志**：记录所有关键操作（仅管理员可见）
- **数据导出**：支持导出路口、点位、项目数据为CSV格式
- **质保状态自动计算**：基于视图实时计算质保状态

## 技术栈

- 后端：Python Flask
- 数据库：MySQL 5.7+
- 前端：HTML5 + Bootstrap 5 + jQuery

## 项目结构

```
smart_traffic/
├── app.py                 # Flask主程序
├── db_config.py           # 数据库配置
├── init_database.sql      # 数据库初始化脚本
├── requirements.txt       # Python依赖
├── README.md              # 使用说明文档
├── static/
│   └── css/
│       └── style.css      # 自定义样式
├── templates/
│   ├── base.html          # 基础模板
│   ├── login.html         # 登录页面
│   ├── index.html         # 路口列表
│   ├── intersection_detail.html  # 路口详情
│   ├── point_list.html    # 点位列表
│   ├── project_list.html  # 项目列表
│   └── log_list.html      # 操作日志
└── uploads/               # 附件存储目录
```

## 快速开始

### 1. 数据库配置

确保MySQL已安装并运行，执行初始化脚本：

```bash
mysql -u root -p < init_database.sql
```

### 2. 数据库连接配置

数据库连接支持两种模式：

**方式一：使用环境变量（推荐）**

```bash
export DB_HOST=localhost          # 数据库主机地址
export DB_PORT=3306               # 数据库端口
export DB_USER=root               # 数据库用户名
export DB_PASSWORD=your_password  # 数据库密码
export DB_NAME=smart_traffic      # 数据库名称
```

**方式二：直接修改配置文件**

编辑 `db_config.py`，修改默认连接信息：

```python
def get_db_connection():
    return pymysql.connect(
        host='localhost',           # 数据库主机地址
        port=3306,                  # 数据库端口
        user='root',                # 数据库用户名
        password='your_password',   # 数据库密码
        database='smart_traffic',   # 数据库名称
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
```

**局域网部署说明：**
- 本地部署：`DB_HOST=localhost` 或 `DB_HOST=127.0.0.1`
- 局域网部署：`DB_HOST=192.168.1.100`（替换为实际数据库服务器IP）

### 3. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 4. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 使用说明

### 登录

- 首次访问会自动跳转到登录页面
- 默认管理员账号：`admin` / `admin123`
- 登录后可查看用户名和角色

### 角色权限

| 角色 | 权限 |
|------|------|
| 管理员(admin) | 查看所有数据、编辑设备、续保操作、上传附件、查看操作日志 |
| 编辑(editor) | 查看所有数据、编辑设备、续保操作、上传附件 |
| 查看(viewer) | 仅可查看数据 |

### 路口管理

- 查看所有路口及质保状态（在保/过保/无项目）
- 点击路口名称查看详细信息
- 点击"续保"按钮为路口添加续保项目
- 点击"导出Excel"下载CSV格式数据

### 路口详情

- 分为"信号灯设备"、"电子警察"和"附件管理"三个标签页
- 点击"编辑"按钮修改设备配置
- 支持修改所有设备字段
- 在"附件管理"标签页可上传和下载附件

### 点位管理

- 查看违停球和卡口点位信息
- 显示点位质保状态
- 点击"导出Excel"下载数据

### 项目管理

- 查看所有项目信息
- 包括项目名称、验收日期、质保期等
- 点击"导出Excel"下载数据

### 操作日志（仅管理员）

- 查看所有用户的操作记录
- 包括操作类型、实体信息、变更内容等
- 支持分页查看

## 数据库设计

系统包含以下核心表：

- `user`：用户信息
- `operation_log`：操作日志
- `project`：项目信息
- `intersection`：路口信息
- `point`：点位信息
- `traffic_light`：信号灯设备
- `electronic_police`：电子警察设备
- `parking_enforcement`：违停球设备
- `checkpoint`：卡口设备
- `warranty_extension`：续保记录
- `attachment`：附件信息

同时包含两个视图用于计算质保状态：

- `intersection_warranty_status`：路口质保状态
- `point_warranty_status`：点位质保状态

## 扩展建议

- GPS地图展示路口分布
- 用户管理界面（增删改用户）
- 设备状态监控（在线/离线）
- 数据报表生成
- API Token认证

## 许可证

MIT License
