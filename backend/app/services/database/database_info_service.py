#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/26
@description  数据库信息服务层
"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import QueuePool

from ...core.exceptions import APIException
from ...models.database.database_conn_model import DatabaseConnection


class DatabaseInfoService:
    """数据库信息服务类"""
    
    def __init__(self):
        self.connection_pool = {}
    
    def _get_connection_key(self, connection_id):
        """获取连接池的键"""
        return f"conn_{connection_id}"
    
    def _get_connection_engine(self, connection_id):
        """获取或创建数据库连接"""
        connection_key = self._get_connection_key(connection_id)
        
        # 检查连接池中是否已有连接
        if connection_key in self.connection_pool:
            try:
                # 测试连接是否有效
                engine = self.connection_pool[connection_key]
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return engine
            except Exception:
                # 连接无效，从池中移除
                del self.connection_pool[connection_key]
        
        # 获取数据库连接信息
        db_conn = DatabaseConnection.query.filter_by(id=connection_id, is_active=True).first()
        if not db_conn:
            raise APIException('数据库连接不存在或已被禁用', 404)
        
        try:
            # 创建连接字符串
            # 使用 pymysql 作为 MySQL 驱动
            connection_string = f"mysql+pymysql://{db_conn.username}:{db_conn.password}@{db_conn.host}:{db_conn.port}/{db_conn.database}?charset={db_conn.charset}"
            
            # 创建引擎
            engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # 连接前测试连接
                echo=False
            )
            
            # 存储连接
            self.connection_pool[connection_key] = engine
            
            return engine
        
        except Exception as e:
            raise APIException(f'数据库连接失败: {str(e)}', 500)
    
    def _get_connection_engine_without_database(self, connection_id):
        """获取不指定数据库的连接引擎（用于查询数据库列表）"""
        connection_key = f"conn_{connection_id}_no_db"
        
        # 检查连接池中是否已有连接
        if connection_key in self.connection_pool:
            try:
                # 测试连接是否有效
                engine = self.connection_pool[connection_key]
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return engine
            except Exception:
                # 连接无效，从池中移除
                del self.connection_pool[connection_key]
        
        # 获取数据库连接信息
        db_conn = DatabaseConnection.query.filter_by(id=connection_id, is_active=True).first()
        if not db_conn:
            raise APIException('数据库连接不存在或已被禁用', 404)
        
        try:
            # 创建连接字符串，不指定数据库（或使用 mysql 系统数据库）
            # 使用 pymysql 作为 MySQL 驱动
            connection_string = f"mysql+pymysql://{db_conn.username}:{db_conn.password}@{db_conn.host}:{db_conn.port}/mysql?charset={db_conn.charset}"
            
            # 创建引擎
            engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # 连接前测试连接
                echo=False
            )
            
            # 存储连接
            self.connection_pool[connection_key] = engine
            
            return engine
        
        except Exception as e:
            raise APIException(f'数据库连接失败: {str(e)}', 500)
    
    def get_databases(self, connection_id):
        """获取所有数据库列表"""
        try:
            # 使用不指定数据库的连接引擎
            engine = self._get_connection_engine_without_database(connection_id)
            
            with engine.connect() as conn:
                # 查询所有数据库（MySQL）
                result = conn.execute(text("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')"))
                databases = [row[0] for row in result.fetchall()]
                
                return databases
        
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'获取数据库列表失败: {str(e)}', 500)
    
    def get_tables(self, connection_id, database_name, keyword=None):
        """获取指定数据库的所有表，支持关键字模糊搜索"""
        try:
            engine = self._get_connection_engine(connection_id)
            
            # 使用 inspect 获取表信息
            inspector = inspect(engine)
            tables = inspector.get_table_names(schema=database_name) if database_name else inspector.get_table_names()
            
            # 关键字模糊过滤（后端安全的小写包含匹配）
            if keyword:
                kw = str(keyword).strip().lower()
                if kw:
                    tables = [t for t in tables if kw in str(t).lower()]
            
            return tables
        
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'获取数据表列表失败: {str(e)}', 500)
    
    def get_table_structure(self, connection_id, database_name, table_name):
        """获取数据表结构"""
        try:
            engine = self._get_connection_engine(connection_id)
            inspector = inspect(engine)
            
            # 获取列信息
            columns = inspector.get_columns(table_name, schema=database_name)
            
            # 获取主键
            primary_keys = inspector.get_pk_constraint(table_name, schema=database_name)
            
            # 获取索引
            indexes = inspector.get_indexes(table_name, schema=database_name)
            
            return {
                'columns': columns,
                'primary_keys': primary_keys.get('constrained_columns', []) if primary_keys else [],
                'indexes': indexes
            }
        
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'获取数据表结构失败: {str(e)}', 500)
    
    def get_column_unique_values(self, connection_id, database_name, table_name, column_name, limit=1000):
        """获取指定列的所有唯一值（用于筛选）"""
        try:
            engine = self._get_connection_engine(connection_id)
            
            with engine.connect() as conn:
                # 获取列的类型信息，以确定是否需要检查空字符串
                inspector = inspect(engine)
                columns = inspector.get_columns(table_name, schema=database_name)
                column_info = None
                for col in columns:
                    if col['name'] == column_name:
                        column_info = col
                        break
                
                # 构建WHERE条件
                # 对于字符串类型（VARCHAR, CHAR, TEXT等），需要检查空字符串
                # 对于数值、日期时间等类型，只需要检查 IS NOT NULL
                where_conditions = [f"`{column_name}` IS NOT NULL"]
                
                if column_info:
                    column_type = str(column_info['type']).upper()
                    # 判断是否为字符串类型
                    is_string_type = any(
                        str_type in column_type 
                        for str_type in ['VARCHAR', 'CHAR', 'TEXT', 'TINYTEXT', 'MEDIUMTEXT', 'LONGTEXT', 'STRING']
                    )
                    if is_string_type:
                        where_conditions.append(f"`{column_name}` != ''")
                
                where_clause = " AND ".join(where_conditions)
                
                # 查询该列的所有唯一值，限制数量以避免数据过大
                query = text(f"SELECT DISTINCT `{column_name}` FROM `{database_name}`.`{table_name}` WHERE {where_clause} ORDER BY `{column_name}` LIMIT {limit}")
                result = conn.execute(query)
                
                # 获取所有唯一值，过滤掉空值
                values = []
                for row in result.fetchall():
                    val = row[0]
                    if val is not None:
                        # 对于字符串类型，再次过滤空字符串
                        val_str = str(val).strip()
                        if val_str:
                            values.append(val_str)
                
                return {
                    'data': values,
                    'total': len(values),
                    'has_more': len(values) >= limit
                }
        except Exception as e:
            raise APIException(f'获取列唯一值失败: {str(e)}', 500)
    
    def get_table_data(self, connection_id, database_name, table_name, page=1, per_page=50, search=None, filters=None):
        """获取数据表数据（支持分页、搜索和筛选）"""
        try:
            engine = self._get_connection_engine(connection_id)
            
            with engine.connect() as conn:
                # 构建WHERE条件
                where_conditions = []
                
                # 添加筛选条件（多选筛选）
                if filters and isinstance(filters, dict):
                    for column, values in filters.items():
                        if values and isinstance(values, list) and len(values) > 0:
                            # 转义列名和值，防止SQL注入
                            escaped_column = column.replace('`', '``')
                            # 构建IN条件
                            placeholders = []
                            for val in values:
                                # 转义单引号
                                escaped_val = str(val).replace("'", "''")
                                placeholders.append(f"'{escaped_val}'")
                            if placeholders:
                                where_conditions.append(f"`{escaped_column}` IN ({', '.join(placeholders)})")
                
                # 添加搜索条件（如果有）
                if search:
                    # 这里可以添加全局搜索逻辑
                    pass
                
                # 构建WHERE子句
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # 计算总数（应用筛选条件）
                count_query = text(f"SELECT COUNT(*) as total FROM `{database_name}`.`{table_name}` {where_clause}")
                count_result = conn.execute(count_query)
                total = count_result.scalar()
                
                # 获取数据
                # 计算偏移量
                offset = (page - 1) * per_page
                
                # 根据数据库主键排序：若存在主键则按主键倒序；否则不指定排序（遵循数据库默认返回顺序）
                inspector = inspect(engine)
                pk_info = inspector.get_pk_constraint(table_name, schema=database_name) or {}
                pk_columns = pk_info.get('constrained_columns') or []
                order_by = ""
                if pk_columns:
                    # 多主键时，全部按倒序以获得稳定分页
                    quoted_cols = ", ".join([f"`{col}` DESC" for col in pk_columns])
                    order_by = f"ORDER BY {quoted_cols}"
                
                query = text(f"SELECT * FROM `{database_name}`.`{table_name}` {where_clause} {order_by} LIMIT {per_page} OFFSET {offset}")
                result = conn.execute(query)
                
                # 获取列名
                columns = result.keys()
                rows = result.fetchall()
                
                # 转换为字典列表，处理时间字段
                def format_value(val):
                    from datetime import datetime
                    if isinstance(val, datetime):
                        return val.strftime('%Y-%m-%d %H:%M:%S')
                    return val
                
                data = []
                for row in rows:
                    row_dict = {}
                    for col, val in zip(columns, row):
                        row_dict[col] = format_value(val)
                    data.append(row_dict)
                
                return {
                    'data': data,
                    'total': total,
                    'page': page,
                    'per_page': per_page
                }
        
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'获取数据表数据失败: {str(e)}', 500)
    
    def execute_query(self, connection_id, database_name, query):
        """执行自定义SQL查询"""
        try:
            engine = self._get_connection_engine(connection_id)
            
            with engine.connect() as conn:
                # 使用指定数据库
                if database_name:
                    conn.execute(text(f"USE `{database_name}`"))
                
                # 执行查询
                result = conn.execute(text(query))
                
                # 如果是 SELECT 查询，返回结果
                if query.strip().upper().startswith('SELECT'):
                    columns = result.keys()
                    rows = result.fetchall()
                    
                    # 处理时间字段
                    def format_value(val):
                        from datetime import datetime
                        if isinstance(val, datetime):
                            return val.strftime('%Y-%m-%d %H:%M:%S')
                        return val
                    
                    data = []
                    for row in rows:
                        row_dict = {}
                        for col, val in zip(columns, row):
                            row_dict[col] = format_value(val)
                        data.append(row_dict)
                    
                    return {
                        'success': True,
                        'data': data,
                        'columns': list(columns),
                        'row_count': len(data)
                    }
                else:
                    # DML 查询，返回影响行数
                    conn.commit()
                    return {
                        'success': True,
                        'message': '查询执行成功',
                        'rowcount': result.rowcount if hasattr(result, 'rowcount') else 0
                    }
        
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'执行查询失败: {str(e)}', 500)
    
    def close_connection(self, connection_id):
        """关闭数据库连接"""
        connection_key = self._get_connection_key(connection_id)
        if connection_key in self.connection_pool:
            engine = self.connection_pool[connection_key] # 获取数据库引擎
            engine.dispose() # 释放引擎资源
            del self.connection_pool[connection_key] # 删除连接池中的连接
            return {'message': '数据库连接已关闭'}
        return {'message': '连接不存在'}
    
    def _sort_tables_by_foreign_keys(self, inspector, database_name, tables):
        """
        根据外键关系对表进行拓扑排序，优先导出被依赖的表
        :param inspector: SQLAlchemy Inspector对象
        :param database_name: 数据库名
        :param tables: 要排序的表列表
        :return: 排序后的表列表
        """
        if not tables or len(tables) <= 1:
            return tables
        
        # 构建依赖图：
        # dependents[table] = [依赖该表的表列表]（反向图）
        # 例如：如果表A有外键引用表B，则 dependents[B] = [A]
        # 这意味着表B应该先于表A导出
        dependents = {}  # 反向依赖图：哪些表依赖当前表
        in_degree = {}   # 入度：当前表依赖多少个其他表
        
        # 初始化
        for table in tables:
            dependents[table] = []
            in_degree[table] = 0
        
        # 获取每个表的外键关系
        for table in tables:
            try:
                foreign_keys = inspector.get_foreign_keys(table_name=table, schema=database_name)
                for fk in foreign_keys:
                    # fk['referred_table'] 是被引用的表（被依赖的表）
                    referred_table = fk.get('referred_table')
                    if referred_table and referred_table in tables:
                        # 表table依赖表referred_table
                        # 所以表referred_table被表table依赖
                        if table not in dependents[referred_table]:
                            dependents[referred_table].append(table)
                            in_degree[table] = in_degree.get(table, 0) + 1
            except Exception:
                # 如果获取外键失败，跳过该表的外键关系
                continue
        
        # 拓扑排序：使用Kahn算法
        # 找到所有入度为0的表（不依赖其他表的表，应该先导出）
        queue = [table for table in tables if in_degree.get(table, 0) == 0]
        sorted_tables = []
        
        while queue:
            # 取出一个入度为0的表（不依赖其他表的表）
            current_table = queue.pop(0)
            sorted_tables.append(current_table)
            
            # 更新依赖该表的其他表的入度
            for dependent_table in dependents.get(current_table, []):
                in_degree[dependent_table] = in_degree.get(dependent_table, 0) - 1
                if in_degree[dependent_table] == 0 and dependent_table not in sorted_tables:
                    queue.append(dependent_table)
        
        # 如果还有表没有被排序（可能存在循环依赖），将它们添加到末尾
        remaining_tables = [table for table in tables if table not in sorted_tables]
        sorted_tables.extend(remaining_tables)
        
        return sorted_tables
    
    def export_data_to_sql(self, connection_id, database_name, table_name, selected_data, sql_types=None):
        """
        导出选中的数据为SQL文件
        :param connection_id: 连接ID
        :param database_name: 数据库名
        :param table_name: 表名
        :param selected_data: 选中的数据列表（字典列表）
        :param sql_types: SQL类型列表，可选 ['INSERT', 'UPDATE', 'DELETE', 'SELECT']，默认为全部
        :return: SQL字符串
        """
        try:
            if not selected_data or len(selected_data) == 0:
                raise APIException('没有选中任何数据', 400)
            
            engine = self._get_connection_engine(connection_id)
            inspector = inspect(engine)
            
            # 获取表结构，特别是主键信息
            pk_info = inspector.get_pk_constraint(table_name, schema=database_name) or {}
            pk_columns = pk_info.get('constrained_columns') or []
            
            # 获取所有列信息（按照表定义顺序）
            # 使用 INFORMATION_SCHEMA 确保字段顺序与 MySQL 存储顺序完全一致
            with engine.connect() as conn:
                query = text(f"""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table_name 
                    ORDER BY ORDINAL_POSITION
                """)
                result = conn.execute(query, {'schema': database_name, 'table_name': table_name})
                all_columns = [row[0] for row in result]
            
            # 如果查询失败，回退到使用 inspector（兼容性处理）
            if not all_columns:
                columns_info = inspector.get_columns(table_name, schema=database_name)
                all_columns = [col['name'] for col in columns_info]
            
            # 默认生成所有类型的SQL
            if sql_types is None:
                sql_types = ['INSERT', 'UPDATE', 'DELETE', 'SELECT']
            
            sql_lines = []
            sql_lines.append(f"-- 导出时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            sql_lines.append(f"-- 数据库: {database_name}")
            sql_lines.append(f"-- 表名: {table_name}")
            sql_lines.append(f"-- 导出数据条数: {len(selected_data)}")
            sql_lines.append("")
            
            # 辅助函数：转义SQL值
            def escape_sql_value(value):
                """转义SQL值"""
                if value is None:
                    return 'NULL'
                elif isinstance(value, (int, float)):
                    return str(value)
                elif isinstance(value, bool):
                    return '1' if value else '0'
                elif isinstance(value, bytes):
                    return f"0x{value.hex()}"
                else:
                    # 字符串类型，转义单引号和反斜杠
                    value_str = str(value)
                    value_str = value_str.replace('\\', '\\\\')
                    value_str = value_str.replace("'", "\\'")
                    return f"'{value_str}'"
            
            # 生成INSERT语句（按照表结构中的字段顺序）
            if 'INSERT' in sql_types:
                sql_lines.append("-- ==================== INSERT 语句 ====================")
                for row_data in selected_data:
                    columns = []
                    values = []
                    # 严格按照表结构中的字段顺序遍历，确保导出顺序与MySQL存储顺序一致
                    for col in all_columns:
                        if col in row_data:
                            columns.append(f"`{col}`")
                            # created_by 和 updated_by 字段使用 NOW() 函数
                            if col in ('created_by', 'updated_by'):
                                values.append('NOW()')
                            else:
                                values.append(escape_sql_value(row_data[col]))
                    
                    if columns:  # 确保至少有一个字段
                        columns_str = ', '.join(columns)
                        values_str = ', '.join(values)
                        sql_lines.append(f"INSERT INTO `{database_name}`.`{table_name}` ({columns_str}) VALUES ({values_str});")
                sql_lines.append("")
            
            # 生成UPDATE语句
            if 'UPDATE' in sql_types:
                sql_lines.append("-- ==================== UPDATE 语句 ====================")
                for row_data in selected_data:
                    # 构建SET子句
                    set_clauses = []
                    where_clauses = []
                    
                    for col in all_columns:
                        if col in row_data:
                            if col in pk_columns:
                                # 主键用于WHERE子句
                                where_clauses.append(f"`{col}` = {escape_sql_value(row_data[col])}")
                            else:
                                # 非主键用于SET子句
                                # created_by 和 updated_by 字段使用 NOW() 函数
                                if col in ('created_by', 'updated_by'):
                                    set_clauses.append(f"`{col}` = NOW()")
                                else:
                                    set_clauses.append(f"`{col}` = {escape_sql_value(row_data[col])}")
                    
                    if set_clauses and where_clauses:
                        set_str = ', '.join(set_clauses)
                        where_str = ' AND '.join(where_clauses)
                        sql_lines.append(f"UPDATE `{database_name}`.`{table_name}` SET {set_str} WHERE {where_str};")
                sql_lines.append("")
            
            # 生成DELETE语句
            if 'DELETE' in sql_types:
                sql_lines.append("-- ==================== DELETE 语句 ====================")
                for row_data in selected_data:
                    where_clauses = []
                    
                    # 优先使用主键构建WHERE条件
                    if pk_columns:
                        for pk_col in pk_columns:
                            if pk_col in row_data:
                                where_clauses.append(f"`{pk_col}` = {escape_sql_value(row_data[pk_col])}")
                    else:
                        # 如果没有主键，使用所有字段构建WHERE条件
                        for col in all_columns:
                            if col in row_data:
                                where_clauses.append(f"`{col}` = {escape_sql_value(row_data[col])}")
                    
                    if where_clauses:
                        where_str = ' AND '.join(where_clauses)
                        sql_lines.append(f"DELETE FROM `{database_name}`.`{table_name}` WHERE {where_str};")
                sql_lines.append("")
            
            # 生成SELECT语句
            if 'SELECT' in sql_types:
                sql_lines.append("-- ==================== SELECT 语句 ====================")
                # 构建所有列的列表
                columns_str = ', '.join([f"`{col}`" for col in all_columns])
                for row_data in selected_data:
                    where_clauses = []
                    
                    # 优先使用主键构建WHERE条件
                    if pk_columns:
                        for pk_col in pk_columns:
                            if pk_col in row_data:
                                where_clauses.append(f"`{pk_col}` = {escape_sql_value(row_data[pk_col])}")
                    else:
                        # 如果没有主键，使用所有字段构建WHERE条件
                        for col in all_columns:
                            if col in row_data:
                                where_clauses.append(f"`{col}` = {escape_sql_value(row_data[col])}")
                    
                    if where_clauses:
                        where_str = ' AND '.join(where_clauses)
                        sql_lines.append(f"SELECT {columns_str} FROM `{database_name}`.`{table_name}` WHERE {where_str};")
                sql_lines.append("")
            
            return '\n'.join(sql_lines)
        
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'导出SQL失败: {str(e)}', 500)
    
    def export_databases_to_sql(self, connection_id, database_tables, sql_types=None):
        """
        导出多个数据库为SQL文件（包括表结构和数据）
        :param connection_id: 连接ID
        :param database_tables: 数据库和表的映射关系，格式: {db_name: [table1, table2, ...]} 或 {db_name: None}（None表示导出所有表）
        :param sql_types: SQL类型列表，可选 ['CREATE', 'INSERT', 'UPDATE', 'DELETE', 'SELECT']，默认为全部
        :return: SQL字符串
        """
        try:
            if not database_tables or len(database_tables) == 0:
                raise APIException('没有选择任何数据库', 400)
            
            engine = self._get_connection_engine(connection_id)
            inspector = inspect(engine)
            
            # 默认生成所有类型的SQL
            if sql_types is None:
                sql_types = ['CREATE', 'INSERT', 'UPDATE', 'DELETE', 'SELECT']
            
            sql_lines = []
            sql_lines.append(f"-- ==================== 数据库导出SQL ====================")
            sql_lines.append(f"-- 导出时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 构建导出信息
            db_info = []
            for db_name, tables in database_tables.items():
                if tables and len(tables) > 0:
                    db_info.append(f"{db_name}({len(tables)}个表)")
                else:
                    db_info.append(f"{db_name}(所有表)")
            sql_lines.append(f"-- 数据库列表: {', '.join(db_info)}")
            sql_lines.append(f"-- 导出类型: {', '.join(sql_types)}")
            sql_lines.append("")
            
            # 辅助函数：转义SQL值
            def escape_sql_value(value):
                """转义SQL值"""
                if value is None:
                    return 'NULL'
                elif isinstance(value, (int, float)):
                    return str(value)
                elif isinstance(value, bool):
                    return '1' if value else '0'
                elif isinstance(value, bytes):
                    return f"0x{value.hex()}"
                else:
                    # 字符串类型，转义单引号和反斜杠
                    value_str = str(value)
                    value_str = value_str.replace('\\', '\\\\')
                    value_str = value_str.replace("'", "\\'")
                    return f"'{value_str}'"
            
            with engine.connect() as conn:
                for db_name, selected_tables in database_tables.items():
                    sql_lines.append("")
                    sql_lines.append(f"-- ==================== 数据库: {db_name} ====================")
                    sql_lines.append("")
                    
                    # 获取该数据库的所有表
                    all_tables = inspector.get_table_names(schema=db_name)
                    
                    if not all_tables:
                        sql_lines.append(f"-- 数据库 {db_name} 中没有表")
                        sql_lines.append("")
                        continue
                    
                    # 如果selected_tables为None或空列表，导出所有表；否则只导出选中的表
                    if selected_tables and len(selected_tables) > 0:
                        tables_to_export = [t for t in selected_tables if t in all_tables]
                        if not tables_to_export:
                            sql_lines.append(f"-- 数据库 {db_name} 中没有选中的表")
                            sql_lines.append("")
                            continue
                    else:
                        tables_to_export = all_tables
                    
                    # 根据外键关系对表进行拓扑排序，优先导出被依赖的表
                    tables_to_export = self._sort_tables_by_foreign_keys(inspector, db_name, tables_to_export)
                    
                    for table_name in tables_to_export:
                        sql_lines.append("")
                        sql_lines.append(f"-- ==================== 表: {table_name} ====================")
                        sql_lines.append("")
                        
                        # 获取表结构
                        if 'CREATE' in sql_types:
                            # 获取CREATE TABLE语句
                            create_table_result = conn.execute(text(f"SHOW CREATE TABLE `{db_name}`.`{table_name}`"))
                            create_row = create_table_result.fetchone()
                            if create_row and len(create_row) >= 2:
                                create_sql = create_row[1]
                                sql_lines.append(f"-- CREATE TABLE 语句")
                                sql_lines.append(f"DROP TABLE IF EXISTS `{db_name}`.`{table_name}`;")
                                sql_lines.append(f"{create_sql};")
                                sql_lines.append("")
                        
                        # 获取表列信息（按照表定义顺序）
                        # 使用 INFORMATION_SCHEMA 确保字段顺序与 MySQL 存储顺序完全一致
                        query = text(f"""
                            SELECT COLUMN_NAME 
                            FROM INFORMATION_SCHEMA.COLUMNS 
                            WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table_name 
                            ORDER BY ORDINAL_POSITION
                        """)
                        result = conn.execute(query, {'schema': db_name, 'table_name': table_name})
                        all_columns = [row[0] for row in result]
                        
                        # 如果查询失败，回退到使用 inspector（兼容性处理）
                        if not all_columns:
                            columns_info = inspector.get_columns(table_name, schema=db_name)
                            all_columns = [col['name'] for col in columns_info]
                        
                        # 获取主键信息
                        pk_info = inspector.get_pk_constraint(table_name, schema=db_name) or {}
                        pk_columns = pk_info.get('constrained_columns', [])
                        
                        # 获取表的所有数据（分批获取，避免内存过大）
                        # 先查询表的总行数
                        total_rows = 0
                        if 'INSERT' in sql_types:
                            count_query = text(f"SELECT COUNT(*) as total FROM `{db_name}`.`{table_name}`")
                            count_result = conn.execute(count_query)
                            total_rows = count_result.scalar() or 0
                        
                        batch_size = 1000
                        offset = 0
                        has_data = True
                        
                        while has_data:
                            query = text(f"SELECT * FROM `{db_name}`.`{table_name}` LIMIT {batch_size} OFFSET {offset}")
                            result = conn.execute(query)
                            rows = result.fetchall()
                            
                            if not rows:
                                has_data = False
                                break
                            
                            # 转换为字典列表，处理时间字段
                            def format_value(val):
                                from datetime import datetime
                                if isinstance(val, datetime):
                                    return val.strftime('%Y-%m-%d %H:%M:%S')
                                return val
                            
                            data = []
                            for row in rows:
                                row_dict = {}
                                for col, val in zip(all_columns, row):
                                    row_dict[col] = format_value(val)
                                data.append(row_dict)
                            
                            # 生成INSERT语句（按照表结构中的字段顺序）
                            if 'INSERT' in sql_types and data:
                                if offset == 0:
                                    sql_lines.append(f"-- INSERT 语句（表: {table_name}）共导出 {total_rows} 条数据")
                                for row_data in data:
                                    columns = []
                                    values = []
                                    # 严格按照表结构中的字段顺序遍历，确保导出顺序与MySQL存储顺序一致
                                    for col in all_columns:
                                        if col in row_data:
                                            columns.append(f"`{col}`")
                                            # created_at 和 updated_at 字段使用 NOW() 函数
                                            if col in ('created_at', 'updated_at'):
                                                values.append('NOW()')
                                            else:
                                                values.append(escape_sql_value(row_data[col]))
                                    
                                    if columns:  # 确保至少有一个字段
                                        columns_str = ', '.join(columns)
                                        values_str = ', '.join(values)
                                        sql_lines.append(f"INSERT INTO `{db_name}`.`{table_name}` ({columns_str}) VALUES ({values_str});")
                            
                            # 生成UPDATE语句
                            if 'UPDATE' in sql_types and data:
                                if offset == 0:
                                    sql_lines.append("")
                                    sql_lines.append(f"-- UPDATE 语句（表: {table_name}）")
                                for row_data in data:
                                    set_clauses = []
                                    where_clauses = []
                                    
                                    for col in all_columns:
                                        if col in row_data:
                                            if col in pk_columns:
                                                where_clauses.append(f"`{col}` = {escape_sql_value(row_data[col])}")
                                            else:
                                                # created_at 和 updated_at 字段使用 NOW() 函数
                                                if col in ('created_at', 'updated_at'):
                                                    set_clauses.append(f"`{col}` = NOW()")
                                                else:
                                                    set_clauses.append(f"`{col}` = {escape_sql_value(row_data[col])}")
                                    
                                    if set_clauses and where_clauses:
                                        set_str = ', '.join(set_clauses)
                                        where_str = ' AND '.join(where_clauses)
                                        sql_lines.append(f"UPDATE `{db_name}`.`{table_name}` SET {set_str} WHERE {where_str};")
                            
                            # 生成DELETE语句
                            if 'DELETE' in sql_types and data:
                                if offset == 0:
                                    sql_lines.append("")
                                    sql_lines.append(f"-- DELETE 语句（表: {table_name}）")
                                for row_data in data:
                                    where_clauses = []
                                    
                                    if pk_columns:
                                        for pk_col in pk_columns:
                                            if pk_col in row_data:
                                                where_clauses.append(f"`{pk_col}` = {escape_sql_value(row_data[pk_col])}")
                                    else:
                                        for col in all_columns:
                                            if col in row_data:
                                                where_clauses.append(f"`{col}` = {escape_sql_value(row_data[col])}")
                                    
                                    if where_clauses:
                                        where_str = ' AND '.join(where_clauses)
                                        sql_lines.append(f"DELETE FROM `{db_name}`.`{table_name}` WHERE {where_str};")
                            
                            # 生成SELECT语句
                            if 'SELECT' in sql_types and data:
                                if offset == 0:
                                    sql_lines.append("")
                                    sql_lines.append(f"-- SELECT 语句（表: {table_name}）")
                                # 构建所有列的列表
                                columns_str = ', '.join([f"`{col}`" for col in all_columns])
                                for row_data in data:
                                    where_clauses = []
                                    
                                    if pk_columns:
                                        for pk_col in pk_columns:
                                            if pk_col in row_data:
                                                where_clauses.append(f"`{pk_col}` = {escape_sql_value(row_data[pk_col])}")
                                    else:
                                        for col in all_columns:
                                            if col in row_data:
                                                where_clauses.append(f"`{col}` = {escape_sql_value(row_data[col])}")
                                    
                                    if where_clauses:
                                        where_str = ' AND '.join(where_clauses)
                                        sql_lines.append(f"SELECT {columns_str} FROM `{db_name}`.`{table_name}` WHERE {where_str};")
                            
                            offset += batch_size
                        
                        if 'INSERT' in sql_types and total_rows > 0:
                            sql_lines.append("")
            
            return '\n'.join(sql_lines)
        
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'导出数据库SQL失败: {str(e)}', 500)

