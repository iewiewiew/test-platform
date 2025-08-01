#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/26
@description  数据库信息管理路由
"""

from flask import Blueprint, request, jsonify

from ...core.exceptions import APIException
from ...services.database.database_info_service import DatabaseInfoService

database_info_bp = Blueprint('database_info', __name__)


@database_info_bp.route('/database-info/<int:connection_id>/databases', methods=['GET'])
def get_databases(connection_id):
    """获取所有数据库列表"""
    try:
        databases = DatabaseInfoService().get_databases(connection_id)
        return jsonify({
            'data': databases,
            'total': len(databases)
        })
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_info_bp.route('/database-info/<int:connection_id>/databases/<database_name>/tables', methods=['GET'])
def get_tables(connection_id, database_name):
    """获取指定数据库的所有表"""
    try:
        keyword = request.args.get('q')
        tables = DatabaseInfoService().get_tables(connection_id, database_name, keyword)
        return jsonify({
            'data': tables,
            'total': len(tables)
        })
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_info_bp.route('/database-info/<int:connection_id>/databases/<database_name>/tables/<table_name>/structure', methods=['GET'])
def get_table_structure(connection_id, database_name, table_name):
    """获取数据表结构"""
    try:
        structure = DatabaseInfoService().get_table_structure(connection_id, database_name, table_name)
        return jsonify(structure)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_info_bp.route('/database-info/<int:connection_id>/databases/<database_name>/tables/<table_name>/columns/<column_name>/unique-values', methods=['GET'])
def get_column_unique_values(connection_id, database_name, table_name, column_name):
    """获取指定列的所有唯一值（用于筛选）"""
    try:
        limit = request.args.get('limit', 1000, type=int)
        result = DatabaseInfoService().get_column_unique_values(connection_id, database_name, table_name, column_name, limit)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_info_bp.route('/database-info/<int:connection_id>/databases/<database_name>/tables/<table_name>/data', methods=['GET'])
def get_table_data(connection_id, database_name, table_name):
    """获取数据表数据（支持分页和筛选）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        search = request.args.get('search')
        # 获取筛选条件（JSON格式）
        filters_json = request.args.get('filters')
        filters = None
        if filters_json:
            import json
            try:
                filters = json.loads(filters_json)
            except json.JSONDecodeError:
                filters = None
        
        result = DatabaseInfoService().get_table_data(connection_id, database_name, table_name, page, per_page, search, filters)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_info_bp.route('/database-info/<int:connection_id>/execute', methods=['POST'])
def execute_query(connection_id):
    """执行自定义SQL查询"""
    try:
        data = request.get_json()
        database_name = data.get('database_name')
        query = data.get('query')
        
        if not query:
            raise APIException('SQL查询不能为空', 400)
        
        result = DatabaseInfoService().execute_query(connection_id, database_name, query)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_info_bp.route('/database-info/<int:connection_id>/close', methods=['POST'])
def close_connection(connection_id):
    """关闭数据库连接"""
    try:
        result = DatabaseInfoService().close_connection(connection_id)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_info_bp.route('/database-info/<int:connection_id>/export-sql', methods=['POST'])
def export_data_to_sql(connection_id):
    """导出选中的数据为SQL文件"""
    try:
        from flask import Response
        
        data = request.get_json()
        database_name = data.get('database_name')
        table_name = data.get('table_name')
        selected_data = data.get('selected_data', [])
        sql_types = data.get('sql_types', None)  # 可选，默认为全部类型
        
        if not database_name or not table_name:
            raise APIException('数据库名和表名不能为空', 400)
        
        if not selected_data:
            raise APIException('没有选中任何数据', 400)
        
        service = DatabaseInfoService()
        sql_content = service.export_data_to_sql(
            connection_id, 
            database_name, 
            table_name, 
            selected_data, 
            sql_types
        )
        
        # 生成文件名
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{database_name}_{table_name}_{timestamp}.sql"
        
        # 返回SQL文件
        response = Response(
            sql_content,
            mimetype='application/sql',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/plain; charset=utf-8'
            }
        )
        return response
        
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('导出SQL失败', 500, {'details': str(e)})


@database_info_bp.route('/database-info/<int:connection_id>/export-databases-sql', methods=['POST'])
def export_databases_to_sql(connection_id):
    """导出多个数据库为SQL文件（包括表结构和数据）"""
    try:
        from flask import Response
        
        data = request.get_json()
        # 支持新格式：database_tables（数据库和表的映射）
        # 也兼容旧格式：database_names（数据库名列表，导出所有表）
        database_tables = data.get('database_tables', {})
        database_names = data.get('database_names', [])
        sql_types = data.get('sql_types', None)  # 可选，默认为全部类型
        
        # 兼容旧格式：如果只有database_names，转换为database_tables格式
        if database_names and len(database_names) > 0:
            if not database_tables:
                database_tables = {db_name: None for db_name in database_names}
        elif not database_tables or len(database_tables) == 0:
            raise APIException('没有选择任何数据库', 400)
        
        service = DatabaseInfoService()
        sql_content = service.export_databases_to_sql(
            connection_id, 
            database_tables, 
            sql_types
        )
        
        # 生成文件名
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_names = list(database_tables.keys())
        db_names_str = '_'.join(db_names[:3])  # 最多取前3个数据库名
        if len(db_names) > 3:
            db_names_str += f"_等{len(db_names)}个"
        filename = f"databases_{db_names_str}_{timestamp}.sql"
        
        # 返回SQL文件
        response = Response(
            sql_content,
            mimetype='application/sql',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/plain; charset=utf-8'
            }
        )
        return response
        
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('导出数据库SQL失败', 500, {'details': str(e)})

