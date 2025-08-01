#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/26
@description  数据库连接管理服务层
"""

from sqlalchemy import or_, text
from sqlalchemy.exc import IntegrityError

from ...core.database import db
from ...core.exceptions import APIException
from ...models.database.database_conn_model import DatabaseConnection


class DatabaseConnService:
    @staticmethod
    def get_all_connections(page=1, per_page=10, name=None, host=None, database=None):
        """获取所有数据库连接（支持分页和搜索）"""
        
        # 基础查询
        query = DatabaseConnection.query.filter_by(is_active=True)
        
        # 添加搜索条件
        conditions = []
        if name:
            conditions.append(DatabaseConnection.name.ilike(f'%{name}%'))
        if host:
            conditions.append(DatabaseConnection.host.ilike(f'%{host}%'))
        if database:
            conditions.append(DatabaseConnection.database.ilike(f'%{database}%'))
        
        # 如果存在搜索条件，应用过滤
        if conditions:
            query = query.filter(or_(*conditions))
        
        # 排序和分页
        pagination = query.order_by(DatabaseConnection.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'data': [conn.to_dict(exclude_password=False) for conn in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    
    @staticmethod
    def get_all_connections_for_select():
        """获取所有数据库连接（用于下拉选择，不分页）"""
        connections = DatabaseConnection.query.filter_by(is_active=True).order_by(DatabaseConnection.name.asc()).all()
        return {
            'data': [conn.to_dict() for conn in connections]
        }
    
    @staticmethod
    def get_connection_by_id(connection_id):
        """获取单个数据库连接详情"""
        
        connection = DatabaseConnection.query.filter_by(id=connection_id, is_active=True).first_or_404()
        return connection.to_dict(exclude_password=False)
    
    @staticmethod
    def create_connection(data, current_user=None):
        """创建数据库连接"""
        
        # 检查必填字段（根据驱动类型不同）
        driver = data.get('driver', 'mysql').lower()
        required_fields = ['name', 'host', 'port']
        
        if driver == 'redis':
            # Redis 不需要 database、username、password（可选）
            pass
        else:
            # MySQL/PostgreSQL 等需要这些字段
            required_fields.extend(['database', 'username', 'password'])
        
        if not all(field in data and data[field] for field in required_fields):
            raise APIException('必填字段不能为空', 400)
        
        try:
            driver = data.get('driver', 'mysql').lower()
            # 根据驱动类型设置默认端口
            default_port = 6379 if driver == 'redis' else 3306
            port = data.get('port') or default_port
            
            connection = DatabaseConnection(
                name=data['name'],
                host=data['host'],
                port=port,
                database=data.get('database'),
                username=data.get('username'),
                password=data.get('password'),
                driver=driver,
                charset=data.get('charset', 'utf8mb4' if driver != 'redis' else ''),
                description=data.get('description', '')
            )
            if current_user:
                connection.created_by = current_user.id
                connection.updated_by = current_user.id
            
            db.session.add(connection)
            db.session.commit()
            
            return connection.to_dict()
        
        except IntegrityError as e:
            db.session.rollback()
            raise APIException('数据库错误', 500, {'details': str(e.orig)})
        except Exception as e:
            db.session.rollback()
            raise APIException('创建数据库连接失败', 500, {'details': str(e)})
    
    @staticmethod
    def update_connection(connection_id, data, current_user=None):
        """更新数据库连接"""
        
        connection = DatabaseConnection.query.filter_by(id=connection_id, is_active=True).first_or_404()
        
        try:
            # 更新字段
            if 'name' in data:
                connection.name = data['name']
            if 'host' in data:
                connection.host = data['host']
            if 'port' in data:
                connection.port = data['port']
            if 'database' in data:
                connection.database = data['database']
            if 'username' in data:
                connection.username = data['username']
            if 'password' in data:
                connection.password = data['password']
            if 'driver' in data:
                connection.driver = data['driver']
            if 'charset' in data:
                connection.charset = data['charset']
            if 'description' in data:
                connection.description = data['description']
            
            if current_user:
                connection.updated_by = current_user.id
            
            db.session.commit()
            
            return connection.to_dict()
        
        except IntegrityError as e:
            db.session.rollback()
            raise APIException('数据库错误', 500, {'details': str(e.orig)})
        except Exception as e:
            db.session.rollback()
            raise APIException('更新数据库连接失败', 500, {'details': str(e)})
    
    @staticmethod
    def delete_connection(connection_id):
        """删除数据库连接（软删除）"""
        
        connection = DatabaseConnection.query.filter_by(id=connection_id, is_active=True).first_or_404()
        
        try:
            # 软删除
            connection.is_active = False
            
            db.session.commit()
            
            return {'message': '数据库连接删除成功'}
        
        except Exception as e:
            db.session.rollback()
            raise APIException('删除失败', 500, {'details': str(e)})
    
    @staticmethod
    def test_connection(connection_id):
        """测试数据库连接"""
        
        connection = DatabaseConnection.query.filter_by(id=connection_id, is_active=True).first_or_404()
        
        try:
            driver = (connection.driver or 'mysql').lower()
            
            if driver == 'redis':
                # 测试 Redis 连接
                import redis
                redis_client = redis.from_url(
                    connection.get_connection_string(),
                    decode_responses=False
                )
                redis_client.ping()
                redis_client.close()
                
                return {
                    'success': True,
                    'message': 'Redis 连接测试成功',
                    'connection': connection.to_dict()
                }
            else:
                # 测试 SQL 数据库连接
                from sqlalchemy import create_engine
                engine = create_engine(connection.get_connection_string())
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                return {
                    'success': True,
                    'message': '数据库连接测试成功',
                    'connection': connection.to_dict()
                }
        except ImportError as e:
            if 'redis' in str(e):
                return {
                    'success': False,
                    'message': 'Redis 连接测试失败: 请先安装 redis 库 (pip install redis)',
                    'connection': connection.to_dict()
                }
            raise
        except Exception as e:
            return {
                'success': False,
                'message': f'数据库连接测试失败: {str(e)}',
                'connection': connection.to_dict()
            }
    
    @staticmethod
    def test_connection_params(data):
        """测试数据库连接参数（不保存）"""
        
        try:
            # 如提供了已有连接ID，则用库中已保存的字段补全（尤其是密码）
            existing = None
            connection_id = data.get('id') or data.get('connection_id')
            if connection_id:
                try:
                    existing = DatabaseConnection.query.filter_by(id=connection_id, is_active=True).first()
                except Exception:
                    existing = None

            # 处理密码：前端常用 ****** 掩码或空字符串，回退到已保存密码
            masked_values = {'******', '*****', '****', None, ''}
            if (not data.get('password') or data.get('password') in masked_values) and existing:
                data['password'] = existing.password

            # 其余字段如未提供则尽量回填，避免拼接出不完整连接串
            fallback_fields = ['host', 'port', 'database', 'username', 'driver', 'charset']
            if existing:
                for f in fallback_fields:
                    if data.get(f) in (None, ''):
                        data[f] = getattr(existing, f)

            # 最终校验必填字段（根据驱动类型）
            driver = data.get('driver', 'mysql').lower()
            required_fields = ['host', 'port']
            
            if driver == 'redis':
                # Redis 不需要 database、username、password（可选）
                pass
            else:
                # MySQL/PostgreSQL 等需要这些字段
                required_fields.extend(['database', 'username', 'password'])
            
            for f in required_fields:
                if not data.get(f) and data.get(f) != 0:
                    raise APIException(f'必填字段不能为空: {f}', 400)
            
            # 测试连接
            if driver == 'redis':
                # 测试 Redis 连接
                try:
                    import redis
                except ImportError:
                    return {
                        'success': False,
                        'message': 'Redis 连接测试失败: 请先安装 redis 库 (pip install redis)'
                    }
                
                connection_string = DatabaseConnService._build_connection_string(data)
                redis_client = redis.from_url(
                    connection_string,
                    decode_responses=False
                )
                redis_client.ping()
                redis_client.close()
                
                return {
                    'success': True,
                    'message': 'Redis 连接测试成功'
                }
            else:
                # 测试 SQL 数据库连接
                connection_string = DatabaseConnService._build_connection_string(data)
                from sqlalchemy import create_engine
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                return {
                    'success': True,
                    'message': '数据库连接测试成功'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'数据库连接测试失败: {str(e)}'
            }

    @staticmethod
    def _build_connection_string(data):
        """
        构建数据库连接字符串

        Args:
            data (dict): 包含连接参数的字典

        Returns:
            str: 数据库连接字符串
        """
        driver = data.get('driver', 'mysql')
        username = data.get('username', '')
        password = data.get('password', '')
        host = data.get('host', '')
        # 根据驱动类型设置默认端口
        default_port = 6379 if driver.lower() == 'redis' else 3306
        port = data.get('port') or default_port
        database = data.get('database', '')
        charset = data.get('charset', 'utf8mb4')
        
        # 统一映射驱动，避免触发 MySQLdb 依赖
        d = (driver or 'mysql').lower()
        
        if d == 'redis':
            # Redis 连接字符串格式: redis://[:password@]host:port[/db]
            if password:
                return f"redis://:{password}@{host}:{port}/{database or 0}"
            else:
                return f"redis://{host}:{port}/{database or 0}"
        elif d in ('mysql', 'pymysql'):
            dialect = 'mysql+pymysql'
        elif d in ('mysqlconnector', 'mysql+mysqlconnector'):
            dialect = 'mysql+mysqlconnector'
        elif d in ('postgresql', 'postgres'):
            dialect = 'postgresql'
        else:
            dialect = 'mysql+pymysql'

        return f"{dialect}://{username}:{password}@{host}:{port}/{database}?charset={charset}"
