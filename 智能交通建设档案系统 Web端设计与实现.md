# 智能交通建设档案系统 - Web端设计与实现

本文档基于前面的数据库设计，提供一个使用 **Python (Flask) + HTML/CSS/JS** 构建的数据展示与操作页面方案。包含路口/点位管理、设备配置、质保状态查看、续保操作、文件上传等核心功能。

---

## 1. 系统架构

- **后端**: Flask (Python 3.8+), PyMySQL, Flask-CORS
- **前端**: HTML5, Bootstrap 5, jQuery, DataTables (可选)
- **数据库**: MySQL 5.7+ / 8.0 (使用前述表结构)

功能模块：
- 路口列表展示（含当前质保状态）
- 路口详情（信号灯、电警设备清单）
- 点位列表展示（违停球、卡口）
- 项目与续保管理
- 附件上传与下载

---

## 2. 环境配置

### 2.1 安装依赖

```bash
pip install flask flask-cors pymysql
```

### 2.2 数据库初始化

执行之前设计的 SQL 建表语句，并插入少量测试数据。

### 2.3 项目目录结构

```
smart_traffic/
├── app.py                 # Flask主程序
├── db_config.py           # 数据库配置
├── static/
│   └── css/
│       └── style.css      # 自定义样式
├── templates/
│   ├── base.html          # 基础模板
│   ├── index.html         # 主页（路口列表）
│   ├── intersection_detail.html  # 路口详情
│   ├── point_list.html    # 点位列表
│   └── project_list.html  # 项目列表
└── uploads/               # 附件存储目录
```

---

## 3. 核心代码实现

### 3.1 数据库配置 `db_config.py`

```python
import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='smart_traffic',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
```

### 3.2 Flask 主程序 `app.py`

```python
from flask import Flask, render_template, request, jsonify, redirect, url_for
import pymysql
from db_config import get_db_connection
from datetime import date

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# 主页：路口列表
@app.route('/')
def index():
    return render_template('index.html')

# API: 获取所有路口及质保状态
@app.route('/api/intersections')
def api_intersections():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM intersection_warranty_status ORDER BY id")
            rows = cur.fetchall()
        return jsonify(rows)
    finally:
        conn.close()

# 路口详情页面
@app.route('/intersection/<int:intersection_id>')
def intersection_detail(intersection_id):
    return render_template('intersection_detail.html', intersection_id=intersection_id)

# API: 获取路口基本信息
@app.route('/api/intersection/<int:intersection_id>')
def api_intersection(intersection_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM intersection WHERE id = %s", (intersection_id,))
            intersection = cur.fetchone()
            # 信号灯设备
            cur.execute("""
                SELECT tl.*, p.name AS project_name, p.warranty_expire_date
                FROM traffic_light tl
                JOIN project p ON tl.project_id = p.id
                WHERE tl.intersection_id = %s
            """, (intersection_id,))
            traffic_lights = cur.fetchall()
            # 电子警察设备
            cur.execute("""
                SELECT ep.*, p.name AS project_name, p.warranty_expire_date
                FROM electronic_police ep
                JOIN project p ON ep.project_id = p.id
                WHERE ep.intersection_id = %s
            """, (intersection_id,))
            electronic_polices = cur.fetchall()
        return jsonify({
            'intersection': intersection,
            'traffic_lights': traffic_lights,
            'electronic_polices': electronic_polices
        })
    finally:
        conn.close()

# 更新信号灯设备
@app.route('/api/traffic_light/<int:tl_id>', methods=['PUT'])
def update_traffic_light(tl_id):
    data = request.json
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                UPDATE traffic_light SET signal_type=%s, signal_count=%s, left_arrow_count=%s,
                straight_arrow_count=%s, right_arrow_count=%s, full_screen_count=%s,
                non_motor_count=%s, pedestrian_count=%s, radar_count=%s, guide_screen_count=%s,
                power_source=%s WHERE id=%s
            """
            cur.execute(sql, (
                data['signal_type'], data['signal_count'], data['left_arrow_count'],
                data['straight_arrow_count'], data['right_arrow_count'], data['full_screen_count'],
                data['non_motor_count'], data['pedestrian_count'], data['radar_count'],
                data['guide_screen_count'], data['power_source'], tl_id
            ))
            conn.commit()
        return jsonify({'status': 'success'})
    finally:
        conn.close()

# 续保操作：为路口添加续保项目
@app.route('/api/intersection/extend_warranty', methods=['POST'])
def extend_warranty():
    data = request.json
    intersection_id = data['intersection_id']
    project_name = data['project_name']
    warranty_expire_date = data['warranty_expire_date']
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 插入新项目
            cur.execute("""
                INSERT INTO project (name, acceptance_date, warranty_expire_date)
                VALUES (%s, %s, %s)
            """, (project_name, date.today(), warranty_expire_date))
            project_id = cur.lastrowid
            # 关联续保表
            cur.execute("""
                INSERT INTO warranty_extension (facility_type, facility_id, project_id, extension_date)
                VALUES (%s, %s, %s, %s)
            """, ('intersection', intersection_id, project_id, date.today()))
            conn.commit()
        return jsonify({'status': 'success', 'project_id': project_id})
    finally:
        conn.close()

# 点位列表页面
@app.route('/points')
def point_list():
    return render_template('point_list.html')

# API: 获取所有点位及质保状态
@app.route('/api/points')
def api_points():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM point_warranty_status ORDER BY id")
            rows = cur.fetchall()
        return jsonify(rows)
    finally:
        conn.close()

# 项目列表页面
@app.route('/projects')
def project_list():
    return render_template('project_list.html')

# API: 获取所有项目
@app.route('/api/projects')
def api_projects():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM project ORDER BY id DESC")
            rows = cur.fetchall()
        return jsonify(rows)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
```

### 3.3 前端模板

#### `templates/base.html`
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能交通档案系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        .warranty-active { color: green; font-weight: bold; }
        .warranty-expired { color: red; }
        .warranty-none { color: gray; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">智能交通档案系统</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">路口管理</a></li>
                    <li class="nav-item"><a class="nav-link" href="/points">点位管理</a></li>
                    <li class="nav-item"><a class="nav-link" href="/projects">项目管理</a></li>
                </ul>
            </div>
        </div>
    </nav>
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

#### `templates/index.html` (路口列表)
```html
{% extends "base.html" %}
{% block content %}
<h2>路口列表</h2>
<table class="table table-bordered table-hover" id="intersectionTable">
    <thead>
        <tr><th>ID</th><th>名称</th><th>类型</th><th>最新质保到期</th><th>状态</th><th>操作</th></tr>
    </thead>
    <tbody></tbody>
</table>

<script>
$(document).ready(function() {
    $.get('/api/intersections', function(data) {
        let rows = '';
        data.forEach(item => {
            let statusClass = '';
            if (item.warranty_status === '在保') statusClass = 'warranty-active';
            else if (item.warranty_status === '过保') statusClass = 'warranty-expired';
            else statusClass = 'warranty-none';
            rows += `<tr>
                <td>${item.id}</td>
                <td><a href="/intersection/${item.id}">${item.name}</a></td>
                <td>${item.type || '-'}</td>
                <td>${item.latest_expire_date || '-'}</td>
                <td class="${statusClass}">${item.warranty_status}</td>
                <td><button class="btn btn-sm btn-primary" onclick="extendWarranty(${item.id})">续保</button></td>
            </tr>`;
        });
        $('#intersectionTable tbody').html(rows);
    });
});

function extendWarranty(id) {
    let projectName = prompt("请输入续保项目名称", "2027年续保");
    if (!projectName) return;
    let expireDate = prompt("请输入质保到期日期 (YYYY-MM-DD)", "2027-12-31");
    if (!expireDate) return;
    $.post('/api/intersection/extend_warranty', JSON.stringify({
        intersection_id: id,
        project_name: projectName,
        warranty_expire_date: expireDate
    }), function(res) {
        if (res.status === 'success') {
            alert("续保成功！");
            location.reload();
        } else {
            alert("失败：" + res.message);
        }
    }).fail(function() {
        alert("请求失败");
    });
}
</script>
{% endblock %}
```

#### `templates/intersection_detail.html` (路口详情)
```html
{% extends "base.html" %}
{% block content %}
<h2 id="intersectionName"></h2>
<ul class="nav nav-tabs" id="myTab" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active" id="traffic-tab" data-bs-toggle="tab" data-bs-target="#traffic" type="button">信号灯设备</button>
    </li>
    <li class="nav-item">
        <button class="nav-link" id="ep-tab" data-bs-toggle="tab" data-bs-target="#ep" type="button">电子警察</button>
    </li>
</ul>
<div class="tab-content mt-3">
    <div class="tab-pane fade show active" id="traffic">
        <table class="table table-sm" id="trafficTable">
            <thead><tr><th>项目</th><th>信号机类型</th><th>信号机数量</th><th>人行灯</th><th>取电说明</th><th>操作</th></tr></thead>
            <tbody></tbody>
        </table>
    </div>
    <div class="tab-pane fade" id="ep">
        <table class="table table-sm" id="epTable">
            <thead><tr><th>项目</th><th>抓拍类型</th><th>正向抓拍</th><th>反向抓拍</th><th>取网说明</th><th>操作</th></tr></thead>
            <tbody></tbody>
        </table>
    </div>
</div>

<script>
const intersectionId = {{ intersection_id }};
$(document).ready(function() {
    $.get(`/api/intersection/${intersectionId}`, function(data) {
        $('#intersectionName').text(data.intersection.name);
        // 信号灯
        let tlRows = '';
        data.traffic_lights.forEach(tl => {
            tlRows += `<tr>
                <td>${tl.project_name} (${tl.warranty_expire_date})</td>
                <td>${tl.signal_type}</td>
                <td>${tl.signal_count}</td>
                <td>${tl.pedestrian_count}</td>
                <td>${tl.power_source || ''}</td>
                <td><button class="btn btn-sm btn-warning" onclick="editTrafficLight(${tl.id})">编辑</button></td>
            </tr>`;
        });
        $('#trafficTable tbody').html(tlRows);
        // 电子警察
        let epRows = '';
        data.electronic_polices.forEach(ep => {
            epRows += `<tr>
                <td>${ep.project_name} (${ep.warranty_expire_date})</td>
                <td>${ep.capture_type}</td>
                <td>${ep.forward_capture_count}</td>
                <td>${ep.reverse_capture_count}</td>
                <td>${ep.network_source || ''}</td>
                <td><button class="btn btn-sm btn-warning" onclick="editElectronicPolice(${ep.id})">编辑</button></td>
            </tr>`;
        });
        $('#epTable tbody').html(epRows);
    });
});

function editTrafficLight(id) {
    // 实际应用中应弹出模态框收集数据，这里简化演示
    let newCount = prompt("修改信号机数量", "");
    if (newCount !== null) {
        $.ajax({
            url: `/api/traffic_light/${id}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({ signal_count: parseInt(newCount) }),
            success: () => location.reload()
        });
    }
}
// 电子警察编辑类似，略
</script>
{% endblock %}
```

#### `templates/point_list.html` (点位列表)
```html
{% extends "base.html" %}
{% block content %}
<h2>点位列表（违停球/卡口）</h2>
<table class="table" id="pointTable">
    <thead><tr><th>ID</th><th>名称</th><th>区域</th><th>最新质保到期</th><th>状态</th></tr></thead>
    <tbody></tbody>
</table>
<script>
$.get('/api/points', function(data) {
    let rows = '';
    data.forEach(p => {
        let cls = p.warranty_status === '在保' ? 'warranty-active' : (p.warranty_status === '过保' ? 'warranty-expired' : 'warranty-none');
        rows += `<tr><td>${p.id}</td><td>${p.name}</td><td>${p.area || '-'}</td><td>${p.latest_expire_date || '-'}</td><td class="${cls}">${p.warranty_status}</td></tr>`;
    });
    $('#pointTable tbody').html(rows);
});
</script>
{% endblock %}
```

#### `templates/project_list.html` (项目列表)
```html
{% extends "base.html" %}
{% block content %}
<h2>所有项目</h2>
<table class="table" id="projectTable">
    <thead><tr><th>ID</th><th>项目名称</th><th>验收日期</th><th>质保到期</th><th>建设单位</th><th>施工单位</th></tr></thead>
    <tbody></tbody>
</table>
<script>
$.get('/api/projects', function(data) {
    let rows = '';
    data.forEach(p => {
        rows += `<tr><td>${p.id}</td><td>${p.name}</td><td>${p.acceptance_date || '-'}</td><td>${p.warranty_expire_date}</td><td>${p.builder || '-'}</td><td>${p.constructor || '-'}</td></tr>`;
    });
    $('#projectTable tbody').html(rows);
});
</script>
{% endblock %}
```

---

## 4. 功能说明

| 页面 | 功能 | 说明 |
|------|------|------|
| 路口列表 | 展示所有路口，含自动计算的质保状态（在保/过保/无项目），提供“续保”按钮 | 续保时弹出输入框，创建新项目并写入 `warranty_extension` 表 |
| 路口详情 | 分为两个标签页，显示该路口下所有信号灯和电子警察设备（来自不同项目） | 支持编辑设备数量（演示级） |
| 点位列表 | 展示违停球/卡口点位及其质保状态 | 基于 `point_warranty_status` 视图 |
| 项目管理 | 列出所有项目，便于查阅质保到期时间和建设/施工单位 | 只读展示 |

> 附件上传功能可在路口详情页增加按钮，调用 `/api/upload` 接口，此处略，但已有 `attachment` 表支持。

---

## 5. 如何运行

1. 确保 MySQL 已启动，并执行了完整的建表 SQL（包含视图）。
2. 修改 `db_config.py` 中的数据库连接参数。
3. 安装 Python 依赖：
   ```bash
   pip install flask flask-cors pymysql
   ```
4. 运行 Flask 应用：
   ```bash
   python app.py
   ```
5. 浏览器访问 `http://127.0.0.1:5000`

---

## 6. 扩展建议

- 增加用户登录与权限管理（Flask-Login）
- 使用 `dropzone.js` 实现拖拽上传附件
- 将视图结果物化为表，提升大量并发查询性能（当前500路口无需）
- 增加设备历史记录表（记录每次变更）
- 对接真实GPS地图展示路口分布

---

## 7. 附录：快速测试数据插入脚本

```sql
INSERT INTO intersection (name, type) VALUES ('人民路与解放路交叉口', '十字路口');
INSERT INTO project (name, acceptance_date, warranty_expire_date, builder, constructor) VALUES 
('2023年信号灯改造', '2023-01-01', '2025-01-01', '市交警支队', 'XX科技公司');
INSERT INTO traffic_light (intersection_id, project_id, signal_type, signal_count, pedestrian_count) 
VALUES (1, 1, '智能', 2, 8);
```

之后查询 `intersection_warranty_status` 即可看到状态。

---

**文档版本**: 1.0  
**最后更新**: 2026-05-25
