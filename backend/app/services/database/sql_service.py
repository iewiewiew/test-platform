#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/22 08:55
@description
"""

import time

import pandas as pd
from flask import current_app
from sqlalchemy import text

from ...core.database import db
from ...core.exceptions import APIException
from ...models.database.sql_model import SQLTemplate, QueryHistory
from .database_info_service import DatabaseInfoService


class SQLService:
    @staticmethod
    def execute_sql(sql_query, limit=1000, connection_id=None, database_name=None, current_user=None):
        """
        执行SQL查询并返回结果
        支持 SELECT, SHOW, DESCRIBE, EXPLAIN 等查询语句
        
        Args:
            sql_query: SQL查询语句
            limit: 结果限制条数
            connection_id: 数据库连接ID（可选，如果不提供则使用默认连接）
            database_name: 数据库名称（可选，仅在指定connection_id时有效）
            current_user: 当前用户对象
        """
        start_time = time.time()
        try:
            # 安全检查：防止DROP、DELETE等危险操作
            dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE TABLE', 'INSERT', 'UPDATE']
            sql_upper = sql_query.upper().strip()

            # 允许的查询类型
            allowed_queries = ['SELECT', 'SHOW', 'DESCRIBE', 'DESC', 'EXPLAIN']

            # 检查是否以允许的查询类型开头
            is_allowed_query = any(sql_upper.startswith(query) for query in allowed_queries)

            if not is_allowed_query:
                # 对于非查询语句，检查是否包含危险关键字
                for keyword in dangerous_keywords:
                    if keyword in sql_upper:
                        raise ValueError(f"出于安全考虑，不允许执行包含 {keyword} 的SQL语句")

            # 根据是否指定连接ID选择执行方式
            if connection_id:
                # 使用指定的数据库连接
                db_info_service = DatabaseInfoService()
                engine = db_info_service._get_connection_engine(connection_id)
                
                with engine.connect() as conn:
                    # 使用指定数据库
                    if database_name:
                        conn.execute(text(f"USE `{database_name}`"))
                    
                    # 执行查询
                    result = conn.execute(text(sql_query))
                    
                    return SQLService._process_query_result(
                        result, sql_upper, limit, sql_query, start_time, 
                        connection_id=connection_id, database_name=database_name, current_user=current_user
                    )
            else:
                # 使用默认数据库连接
                result = db.session.execute(text(sql_query))
                
                return SQLService._process_query_result(
                    result, sql_upper, limit, sql_query, start_time, current_user=current_user
                )

        except APIException:
            raise
        except Exception as e:
            execution_time = time.time() - start_time

            # 保存错误历史（只在使用默认连接时保存）
            if not connection_id:
                try:
                    history = QueryHistory(sql_query=sql_query, execution_time=execution_time, success=False,
                        error_message=str(e))
                    if current_user:
                        history.created_by = current_user.id
                        history.updated_by = current_user.id
                    db.session.add(history)
                    db.session.commit()
                except Exception as save_error:
                    current_app.logger.warning(f"保存错误历史失败: {str(save_error)}")

            return {'success': False, 'error': str(e), 'execution_time': execution_time}

    @staticmethod
    def _process_query_result(result, sql_upper, limit, sql_query, start_time, connection_id=None, database_name=None, current_user=None):
        """
        处理查询结果
        
        Args:
            result: SQL执行结果
            sql_upper: 大写的SQL语句
            limit: 结果限制条数
            sql_query: 原始SQL语句
            start_time: 开始时间
            connection_id: 连接ID（可选）
            database_name: 数据库名称（可选）
            current_user: 当前用户对象
        """
        # 判断是否为返回结果的查询类型
        query_types_with_results = ['SELECT', 'SHOW', 'DESCRIBE', 'DESC', 'EXPLAIN']
        is_result_query = any(sql_upper.startswith(query) for query in query_types_with_results)

        if is_result_query:
            # 获取列名和数据
            columns = [col for col in result.keys()]

            # 对于SHOW语句等，可能需要特殊处理
            if sql_upper.startswith('SHOW DATABASES'):
                # SHOW DATABASES 的特殊处理
                data = result.fetchall()
                # 确保数据格式正确
                if data and len(data[0]) == 1:
                    # 如果返回的是单列元组，转换为字典格式
                    data = [{'Database': row[0]} for row in data]
                    columns = ['Database']
                result_data = {'columns': columns, 'data': data, 'row_count': len(data),
                    'query_type': 'SHOW_DATABASES'}
            elif sql_upper.startswith('SHOW TABLES'):
                # SHOW TABLES 的特殊处理
                data = result.fetchall()
                if data and len(data[0]) == 1:
                    data = [{'Tables_in_database': row[0]} for row in data]
                    columns = ['Tables_in_database']
                result_data = {'columns': columns, 'data': data, 'row_count': len(data),
                    'query_type': 'SHOW_TABLES'}
            elif sql_upper.startswith('SHOW'):
                # 其他SHOW语句
                data = result.fetchmany(limit)
                result_data = {'columns': columns, 'data': data, 'row_count': len(data), 'query_type': 'SHOW'}
            elif sql_upper.startswith('DESCRIBE') or sql_upper.startswith('DESC'):
                # DESCRIBE 表结构查询
                data = result.fetchall()
                result_data = {'columns': columns, 'data': data, 'row_count': len(data), 'query_type': 'DESCRIBE'}
            else:
                # SELECT 和其他查询
                data = result.fetchmany(limit)
                # 转换为字典格式以便前端显示
                try:
                    df = pd.DataFrame(data, columns=columns)
                    data_dict = df.to_dict('records')
                except Exception as df_error:
                    # 如果pandas转换失败，使用原始数据
                    current_app.logger.warning(f"DataFrame转换失败，使用原始数据: {df_error}")
                    data_dict = [dict(zip(columns, row)) for row in data]

                result_data = {'columns': columns, 'data': data_dict, 'row_count': len(data),
                    'query_type': 'SELECT'}
        else:
            # 非查询语句（如 SET, USE 等）
            result_data = {'message': '执行成功', 'affected_rows': result.rowcount, 'query_type': 'NON_QUERY'}

        execution_time = time.time() - start_time

        # 保存查询历史（只在使用默认连接时保存到历史）
        if not connection_id:
            try:
                history = QueryHistory(sql_query=sql_query, execution_time=execution_time, success=True)
                if current_user:
                    history.created_by = current_user.id
                    history.updated_by = current_user.id
                db.session.add(history)
                db.session.commit()
            except Exception as e:
                current_app.logger.warning(f"保存查询历史失败: {str(e)}")

        response = {
            'success': True, 
            'data': result_data, 
            'execution_time': execution_time,
            'sql_type': 'QUERY' if is_result_query else 'NON_QUERY'
        }
        
        if connection_id:
            response['connection_id'] = connection_id
        if database_name:
            response['database'] = database_name
            
        return response

    @staticmethod
    def get_database_info():
        """
        获取数据库基本信息
        """
        try:
            # 获取所有数据库
            databases_result = db.session.execute(text("SHOW DATABASES"))
            databases = [row[0] for row in databases_result.fetchall()]

            # 获取当前数据库
            current_db_result = db.session.execute(text("SELECT DATABASE()"))
            current_db = current_db_result.fetchone()[0] if current_db_result else None

            # 获取版本信息
            version_result = db.session.execute(text("SELECT VERSION()"))
            version = version_result.fetchone()[0] if version_result else None

            return {'databases': databases, 'current_database': current_db, 'version': version}
        except Exception as e:
            current_app.logger.error(f"获取数据库信息失败: {str(e)}")
            return {'databases': [], 'current_database': None, 'version': None, 'error': str(e)}

    @staticmethod
    def get_all_templates():
        """获取所有SQL模板"""
        return SQLTemplate.query.order_by(SQLTemplate.category, SQLTemplate.id.desc()).all()

    @staticmethod
    def get_template_by_id(template_id):
        """根据ID获取SQL模板"""
        return SQLTemplate.query.get(template_id)

    @staticmethod
    def create_template(template_data, current_user=None):
        """创建新的SQL模板"""
        template = SQLTemplate(name=template_data['name'], description=template_data.get('description', ''),
            sql_content=template_data['sql_content'], category=template_data['category'])
        if current_user:
            template.created_by = current_user.id
            template.updated_by = current_user.id
        db.session.add(template)
        db.session.commit()
        return template

    @staticmethod
    def update_template(template_id, template_data, current_user=None):
        """更新SQL模板"""
        template = SQLTemplate.query.get(template_id)
        if not template:
            return None

        template.name = template_data.get('name', template.name)
        template.description = template_data.get('description', template.description)
        template.sql_content = template_data.get('sql_content', template.sql_content)
        template.category = template_data.get('category', template.category)
        
        if current_user:
            template.updated_by = current_user.id

        db.session.commit()
        return template

    @staticmethod
    def delete_template(template_id):
        """删除SQL模板"""
        template = SQLTemplate.query.get(template_id)
        if template:
            db.session.delete(template)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_query_history(limit=50):
        """获取查询历史"""
        return QueryHistory.query.order_by(QueryHistory.id.desc()).limit(limit).all()
