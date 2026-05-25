-- 智能交通建设档案系统数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS smart_traffic CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE smart_traffic;

-- 用户表
CREATE TABLE IF NOT EXISTS user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    display_name VARCHAR(100) COMMENT '显示名称',
    role ENUM('admin', 'editor', 'viewer') DEFAULT 'viewer' COMMENT '角色：管理员/编辑/查看',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT COMMENT '操作用户ID',
    username VARCHAR(50) COMMENT '操作用户名称',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    entity_type VARCHAR(50) COMMENT '操作实体类型',
    entity_id INT COMMENT '操作实体ID',
    old_value TEXT COMMENT '旧值',
    new_value TEXT COMMENT '新值',
    ip_address VARCHAR(50),
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- 项目表
CREATE TABLE IF NOT EXISTS project (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '项目名称',
    contract_amount DECIMAL(15,2) COMMENT '合同金额',
    acceptance_date DATE COMMENT '验收日期',
    warranty_period VARCHAR(50) COMMENT '质保期（如 2年）',
    warranty_expire_date DATE NOT NULL COMMENT '质保到期时间',
    builder VARCHAR(100) COMMENT '建设单位',
    constructor VARCHAR(100) COMMENT '施工单位'
);

-- 路口表
CREATE TABLE IF NOT EXISTS intersection (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '路口名称',
    type ENUM('十字路口', '丁字路口', '行人过街', '其他') COMMENT '路口类型'
);

-- 点位表
CREATE TABLE IF NOT EXISTS point (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '点位名称',
    area VARCHAR(100) COMMENT '抓拍区域（违停球用）',
    type VARCHAR(50) COMMENT '卡口类型或违停球类型'
);

-- 信号灯表
CREATE TABLE IF NOT EXISTS traffic_light (
    id INT PRIMARY KEY AUTO_INCREMENT,
    intersection_id INT NOT NULL COMMENT '路口ID',
    project_id INT NOT NULL COMMENT '所属项目ID',
    signal_type VARCHAR(50) COMMENT '信号机类型（智能/非智能）',
    signal_count INT DEFAULT 0,
    left_arrow_count INT DEFAULT 0,
    straight_arrow_count INT DEFAULT 0,
    right_arrow_count INT DEFAULT 0,
    full_screen_count INT DEFAULT 0,
    non_motor_count INT DEFAULT 0,
    pedestrian_count INT DEFAULT 0,
    radar_count INT DEFAULT 0,
    guide_screen_count INT DEFAULT 0,
    power_source TEXT COMMENT '取电说明',
    FOREIGN KEY (intersection_id) REFERENCES intersection(id),
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- 电子警察表
CREATE TABLE IF NOT EXISTS electronic_police (
    id INT PRIMARY KEY AUTO_INCREMENT,
    intersection_id INT NOT NULL,
    project_id INT NOT NULL,
    capture_type VARCHAR(50) COMMENT '抓拍类型',
    terminal_server_count INT DEFAULT 0,
    forward_capture_count INT DEFAULT 0,
    reverse_capture_count INT DEFAULT 0,
    led_light_count INT DEFAULT 0,
    strobe_light_count INT DEFAULT 0,
    ptz_count INT DEFAULT 0,
    signal_detector_count INT DEFAULT 0,
    network_source TEXT COMMENT '取网说明',
    FOREIGN KEY (intersection_id) REFERENCES intersection(id),
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- 违停球表
CREATE TABLE IF NOT EXISTS parking_enforcement (
    id INT PRIMARY KEY AUTO_INCREMENT,
    point_id INT NOT NULL,
    project_id INT NOT NULL,
    camera_count INT DEFAULT 0,
    parking_sign_count INT DEFAULT 0,
    monitor_sign_count INT DEFAULT 0,
    power_source TEXT,
    network_source TEXT,
    FOREIGN KEY (point_id) REFERENCES point(id),
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- 卡口表
CREATE TABLE IF NOT EXISTS checkpoint (
    id INT PRIMARY KEY AUTO_INCREMENT,
    point_id INT NOT NULL,
    project_id INT NOT NULL,
    camera_count INT DEFAULT 0,
    strobe_light_count INT DEFAULT 0,
    radar_count INT DEFAULT 0,
    sign_count INT DEFAULT 0,
    power_source TEXT,
    network_source TEXT,
    FOREIGN KEY (point_id) REFERENCES point(id),
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- 后端设备表
CREATE TABLE IF NOT EXISTS backend_device (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) COMMENT '设备类型（网络交换设备、服务器等）',
    project_id INT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- 续保记录表
CREATE TABLE IF NOT EXISTS warranty_extension (
    id INT PRIMARY KEY AUTO_INCREMENT,
    facility_type ENUM('intersection', 'point') NOT NULL COMMENT '设施类型',
    facility_id INT NOT NULL COMMENT '路口ID或点位ID',
    project_id INT NOT NULL COMMENT '续保项目ID',
    extension_date DATE NOT NULL COMMENT '续保生效日期',
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- 附件表
CREATE TABLE IF NOT EXISTS attachment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    related_entity_type ENUM('project', 'intersection', 'point', 'traffic_light', 'electronic_police', 'parking_enforcement', 'checkpoint', 'backend_device') NOT NULL,
    related_entity_id INT NOT NULL COMMENT '对应表的记录ID',
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT COMMENT '字节数',
    mime_type VARCHAR(100),
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100),
    description TEXT
);

-- 创建路口质保状态视图
CREATE OR REPLACE VIEW intersection_warranty_status AS
WITH all_intersection_projects AS (
    SELECT intersection_id, project_id FROM traffic_light
    UNION
    SELECT intersection_id, project_id FROM electronic_police
    UNION
    SELECT facility_id AS intersection_id, project_id FROM warranty_extension WHERE facility_type = 'intersection'
)
SELECT
    i.id,
    i.name,
    i.type,
    MAX(p.warranty_expire_date) AS latest_expire_date,
    CASE
        WHEN MAX(p.warranty_expire_date) >= CURDATE() THEN '在保'
        WHEN MAX(p.warranty_expire_date) IS NULL THEN '无项目'
        ELSE '过保'
    END AS warranty_status
FROM intersection i
LEFT JOIN all_intersection_projects aip ON i.id = aip.intersection_id
LEFT JOIN project p ON aip.project_id = p.id
GROUP BY i.id, i.name, i.type;

-- 创建点位质保状态视图
CREATE OR REPLACE VIEW point_warranty_status AS
WITH all_point_projects AS (
    SELECT point_id, project_id FROM parking_enforcement
    UNION
    SELECT point_id, project_id FROM checkpoint
    UNION
    SELECT facility_id AS point_id, project_id FROM warranty_extension WHERE facility_type = 'point'
)
SELECT
    p.id,
    p.name,
    p.area,
    p.type,
    MAX(proj.warranty_expire_date) AS latest_expire_date,
    CASE
        WHEN MAX(proj.warranty_expire_date) >= CURDATE() THEN '在保'
        WHEN MAX(proj.warranty_expire_date) IS NULL THEN '无项目'
        ELSE '过保'
    END AS warranty_status
FROM point p
LEFT JOIN all_point_projects app ON p.id = app.point_id
LEFT JOIN project proj ON app.project_id = proj.id
GROUP BY p.id, p.name, p.area, p.type;

-- 插入默认管理员用户 (密码: admin123)
-- 密码哈希: pbkdf2:sha256:600000$salt$vXKXMdJd$5a8f3d2b1c4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
INSERT INTO user (username, password_hash, display_name, role) VALUES
('admin', 'pbkdf2:sha256:600000$vXKXMdJd$5a8f3d2b1c4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0', '系统管理员', 'admin');

-- 插入测试数据
INSERT INTO intersection (name, type) VALUES ('人民路与解放路交叉口', '十字路口');
INSERT INTO intersection (name, type) VALUES ('建设路与公园路交叉口', '丁字路口');

INSERT INTO point (name, area, type) VALUES ('市政府广场违停球', '广场周边', '违停球');
INSERT INTO point (name, area, type) VALUES ('高速出口卡口', '高速路出口', '卡口');

INSERT INTO project (name, acceptance_date, warranty_period, warranty_expire_date, builder, constructor) VALUES
('2023年信号灯改造', '2023-01-01', '2年', '2027-01-01', '市交警支队', 'XX科技公司');

INSERT INTO traffic_light (intersection_id, project_id, signal_type, signal_count, pedestrian_count, power_source)
VALUES (1, 1, '智能', 2, 8, '市电');

INSERT INTO electronic_police (intersection_id, project_id, capture_type, forward_capture_count, network_source)
VALUES (1, 1, '闯红灯', 4, '光纤专线');
