-- ============================================
-- 智能交通管理系统 数据库变更脚本（MySQL）
-- 日期：2026-06-04
-- 用法：mysql -u用户名 -p 数据库名 < migration_20260604.sql
-- ============================================

-- backend_device 表新增 品牌型号 字段
ALTER TABLE backend_device
  ADD COLUMN model VARCHAR(100) DEFAULT NULL COMMENT '设备品牌型号';

-- backend_device 表新增 设备数量 字段
ALTER TABLE backend_device
  ADD COLUMN quantity INT NOT NULL DEFAULT 1 COMMENT '设备数量';
