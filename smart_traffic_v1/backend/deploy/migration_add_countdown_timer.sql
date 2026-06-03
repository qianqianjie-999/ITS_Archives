-- 数据库迁移脚本：为traffic_light表添加倒计时器数量字段
-- 执行方式: mysql -u root -p smart_traffic < migration_add_countdown_timer.sql

ALTER TABLE `traffic_light`
ADD COLUMN `countdown_timer_count` INT(11) NOT NULL DEFAULT 0 COMMENT '倒计时器数量'
AFTER `pedestrian_count`;

-- 验证字段是否添加成功
DESCRIBE `traffic_light`;