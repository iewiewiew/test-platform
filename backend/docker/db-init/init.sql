-- mysql -h127.0.0.1 -uroot -p123456
-- 删除数据库 drop database test_platform;
-- 创建数据库 CREATE DATABASE IF NOT EXISTS test_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- 清空数据 truncate `test_platform`.`examples`;
-- 删除数据 drop table `test_platform`.`examples`

-- 临时禁用外键检查，允许插入数据后再创建用户
SET FOREIGN_KEY_CHECKS = 0;

-- 示例数据
INSERT INTO `test_platform`.`examples` (id, name, description, status, created_at, updated_at, is_active, created_by, updated_by) VALUES(1, '示例名称1', '描述1', 'active', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`examples` (id, name, description, status, created_at, updated_at, is_active, created_by, updated_by) VALUES(2, '示例名称2', '描述2', 'inactive', NOW(),NOW(), 1, 1, 1);

-- 项目示例数据
INSERT INTO `test_platform`.`projects` (name,description,created_at,updated_at,is_active,created_by,updated_by) VALUES ('示例项目1','',NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`projects` (name,description,created_at,updated_at,is_active,created_by,updated_by) VALUES ('示例项目2','',NOW(),NOW(), 1, 1, 1);

-- Mock接口示例数据
INSERT INTO `test_platform`.mocks (name,`path`,`method`,response_status,response_body,description,project_id,created_at,updated_at,is_active,created_by,updated_by) VALUES ('GET接口示例','/api/users','GET',200,'{"users": [{"id": 1}]}','','1',NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.mocks (name,`path`,`method`,response_status,response_body,description,project_id,created_at,updated_at,is_active,created_by,updated_by) VALUES ('POST接口示例','/api/users','POST',201,'{"request_id":"{request.json.id}","req_str":"{request.json.req_str}","action":"{request.args.action}","email":"${email}","example":"示例"}','','1',NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.mocks (name,`path`,`method`,response_status,response_body,description,project_id,created_at,updated_at,is_active,created_by,updated_by) VALUES ('PUT接口示例','/api/users/1','PUT',200,'{"request_id":"{request.json.id}","req_str":"{request.json.req_str}","action":"{request.args.action}","email":"${email}","example":"示例"}','','1',NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.mocks (name,`path`,`method`,response_status,response_body,description,project_id,created_at,updated_at,is_active,created_by,updated_by) VALUES ('DELETE接口示例','/api/users/1','DELETE',204,'"delete success"','','1',NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.mocks (name,`path`,`method`,response_status,response_body,description,project_id,created_at,updated_at,is_active,created_by,updated_by) VALUES ('随机数接口示例','/api/example','GET',200,'{"user":{"id":"${uuid}","name":"${name}","email":"${email}","phone":"${phone}","birthday":"${date[%Y-%m-%d,1990-01-01,2000-12-31]}","salary":"${float[5000,20000,2]}","address":"${address}","company":"${company}","avatar":"${image_url}"},"current_time":"${now}","current_date":"${now[%Y-%m-%d]}","timestamp":"${now[%Y%m%d%H%M%S]}"}','','1',NOW(),NOW(), 1, 1, 1);

-- 环境示例数据
INSERT INTO `test_platform`.`environments` (id, name, base_url, username, password, description, parameter_count, created_at, updated_at, is_active, created_by, updated_by) VALUES(1, 'Dev环境', 'http://www.dev.com', 'admin', '123456', '开发环境', 0, NOW(), NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`environments` (id, name, base_url, username, password, description, parameter_count, created_at, updated_at, is_active, created_by, updated_by) VALUES(2, 'Test环境', 'http://www.test.com', 'admin', '123456', '测试环境', 0, NOW(), NOW(), 1, 1, 1);

-- 服务器示例数据
INSERT INTO `test_platform`.`linux_servers` (id, server_name,host,port,username,password,private_key,description,created_at,updated_at,is_active,created_by,updated_by) VALUES(1, '服务器示例','127.0.0.1',22,'root','123456','','',NOW(),NOW(), 1, 1, 1);

-- 数据库连接示例数据
INSERT INTO `test_platform`.`database_connections` (id, name, host, port, `database`, username, password, driver, charset, description, is_active, created_at, updated_at, created_by, updated_by) VALUES(1, '本地MySQL', '127.0.0.1', 3306, 'test_platform', 'root', '123456', 'mysql', 'utf8mb4', '', 1, NOW(),NOW(), 1, 1);
-- 复制到 backend/docker/db-init/init.sql 需删除此行

-- SQL模板示例数据
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(1, '查询数据库', '显示所有数据库', 'show databases;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(2, '查询数据表', '显示当前数据库的所有表', 'show tables;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(3, '查询表结构', '显示表的字段信息', 'desc table_name;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(4, '查询表数据', '查询表中的所有数据', 'select * from table_name;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(5, '条件查询', '带条件的查询语句', 'select * from table_name where condition;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(6, '分页查询', '分页查询数据', 'select * from table_name limit 10 offset 0;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(7, '排序查询', '按字段排序查询', 'select * from table_name order by column_name desc;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(8, '插入数据', '插入单条数据', 'insert into table_name (col1, col2) values (value1, value2);', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(9, '批量插入', '批量插入多条数据', 'insert into table_name (col1, col2) values (value1, value2), (value3, value4);', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(10, '更新数据', '更新表中的数据', 'update table_name set column1 = value1 where condition;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(11, '删除数据', '删除表中的数据', 'delete from table_name where condition;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(12, '创建数据库', '创建新的数据库', 'create database db_name;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(13, '创建数据表', '创建新的数据表', 'create table table_name (id int primary key, name varchar(50));', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(14, '添加字段', '为表添加新字段', 'alter table table_name add column new_column varchar(100);', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(15, '删除表', '删除数据表', 'drop table table_name;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(16, '表连接查询', '多表连接查询', 'select a.*, b.* from table_a a join table_b b on a.id = b.a_id;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(17, '分组统计', '分组统计查询', 'select column, count(*) from table_name group by column;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(18, '子查询', '使用子查询', 'select * from table_name where id in (select id from other_table);', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(19, '创建索引', '为表创建索引', 'create index idx_name on table_name(column_name);', '示例模板SQL', NOW(),NOW(), 1, 1, 1);
INSERT INTO `test_platform`.`sql_templates` (id, name, description, sql_content, category, created_at, updated_at, is_active, created_by, updated_by) VALUES(20, '查询执行计划', '查看SQL执行计划', 'explain select * from table_name;', '示例模板SQL', NOW(),NOW(), 1, 1, 1);

INSERT INTO test_platform.images (filename, original_filename, file_path, file_size, mime_type, width, height, description, tags, url, id, is_active, created_by, updated_by, created_at, updated_at) VALUES('1104170722082024-600x400.jpg', '1104170722082024-600x400.jpg', '/root/test-platform/backend/static/images/1104170722082024-600x400.jpg', 74149, 'image/jpeg', 600, 400, NULL, NULL, '/api/images/1104170722082024-600x400.jpg', 1, 1, NULL, NULL, NOW(), NOW());
INSERT INTO test_platform.images (filename, original_filename, file_path, file_size, mime_type, width, height, description, tags, url, id, is_active, created_by, updated_by, created_at, updated_at) VALUES('laohuji.jpg', 'laohuji.jpg', '/root/test-platform/backend/static/images/laohuji.jpg', 143350, 'image/jpeg', 750, 500, NULL, NULL, '/api/images/laohuji.jpg', 2, 1, NULL, NULL, NOW(), NOW());
INSERT INTO test_platform.images (filename, original_filename, file_path, file_size, mime_type, width, height, description, tags, url, id, is_active, created_by, updated_by, created_at, updated_at) VALUES('GettyImages-987472756.jpg', 'GettyImages-987472756.jpg', '/root/test-platform/backend/static/images/GettyImages-987472756.jpg', 4348430, 'image/jpeg', 5318, 3203, NULL, NULL, '/api/images/GettyImages-987472756.jpg', 3, 1, NULL, NULL, NOW(), NOW());
INSERT INTO test_platform.images (filename, original_filename, file_path, file_size, mime_type, width, height, description, tags, url, id, is_active, created_by, updated_by, created_at, updated_at) VALUES('211_19077_871275.jpg', '211_19077_871275.jpg', '/root/test-platform/backend/static/images/211_19077_871275.jpg', 107974, 'image/jpeg', 700, 467, NULL, NULL, '/api/images/211_19077_871275.jpg', 4, 1, NULL, NULL, NOW(), NOW());

-- 脚本管理示例数据
INSERT INTO test_platform.scripts (name, description, script_type, script_content, file_path, is_enabled, timeout_seconds, environment_vars, is_scheduled, cron_expression, schedule_job_id, total_executions, success_count, failure_count, id, created_at, updated_at, is_active, created_by, updated_by) VALUES ('Python脚本示例', '', 'python', '#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys

def main():
    print(\'Hello World\')

if __name__ == \'__main__\':
    main()
', null, 1, 300, null, 0, '', null, 0, 0, 0, 0, NOW(),NOW(), 1, 1, 1);
INSERT INTO test_platform.scripts (name, description, script_type, script_content, file_path, is_enabled, timeout_seconds, environment_vars, is_scheduled, cron_expression, schedule_job_id, total_executions, success_count, failure_count, id, created_at, updated_at, is_active, created_by, updated_by) VALUES ('Shell脚本示例', '', 'shell', '#!/bin/bash

echo "Hello World"
', null, 1, 300, null, 0, '', null, 0, 0, 0, 0, NOW(),NOW(), 1, 1, 1);

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;