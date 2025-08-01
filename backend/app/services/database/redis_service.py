#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/26
@description  Redis 数据库服务层
"""

import redis
from typing import List, Dict, Any, Optional

from ...core.exceptions import APIException
from ...models.database.database_conn_model import DatabaseConnection


class RedisService:
    """Redis 数据库服务类"""
    
    def __init__(self):
        self.connection_pool = {}
    
    def _get_connection_key(self, connection_id):
        """获取连接池的键"""
        return f"redis_{connection_id}"
    
    def _get_redis_client(self, connection_id):
        """获取或创建 Redis 连接"""
        connection_key = self._get_connection_key(connection_id)
        
        # 检查连接池中是否已有连接
        if connection_key in self.connection_pool:
            try:
                client = self.connection_pool[connection_key]
                client.ping()
                return client
            except Exception:
                # 连接无效，从池中移除
                del self.connection_pool[connection_key]
        
        # 获取数据库连接信息
        db_conn = DatabaseConnection.query.filter_by(id=connection_id, is_active=True).first()
        
        if not db_conn:
            raise APIException('数据库连接不存在或已被禁用', 404)
        
        if db_conn.driver.lower() != 'redis':
            raise APIException('该连接不是 Redis 类型', 400)
        
        try:
            # 构建 Redis 连接参数
            redis_url = db_conn.get_connection_string()
            
            # 创建 Redis 客户端
            client = redis.from_url(
                redis_url,
                decode_responses=False,  # 不自动解码，保持原始字节
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # 测试连接
            client.ping()
            
            # 存储连接
            self.connection_pool[connection_key] = client
            
            return client
        
        except ImportError:
            raise APIException('Redis 连接失败: 请先安装 redis 库 (pip install redis)', 500)
        except Exception as e:
            raise APIException(f'Redis 连接失败: {str(e)}', 500)
    
    def get_keys(self, connection_id, pattern='*', cursor=0, count=100):
        """获取 Redis keys（支持分页）"""
        try:
            client = self._get_redis_client(connection_id)
            
            # 使用 SCAN 命令进行分页扫描
            keys = []
            next_cursor = cursor
            
            while True:
                cursor_result = client.scan(cursor=next_cursor, match=pattern, count=count)
                next_cursor, batch_keys = cursor_result
                keys.extend([key.decode('utf-8') if isinstance(key, bytes) else key for key in batch_keys])
                
                # 如果返回的 cursor 为 0，说明扫描完成
                if next_cursor == 0:
                    break
                
                # 如果已经获取了足够的 keys，可以提前退出
                if len(keys) >= count:
                    break
            
            # 限制返回数量
            keys = keys[:count]
            
            return {
                'keys': keys,
                'cursor': next_cursor,
                'count': len(keys),
                'has_more': next_cursor != 0
            }
        except Exception as e:
            raise APIException(f'获取 Redis keys 失败: {str(e)}', 500)
    
    def get_key_info(self, connection_id, key: str):
        """获取 key 的详细信息（类型、TTL、值等）"""
        try:
            client = self._get_redis_client(connection_id)
            
            # 检查 key 是否存在
            if not client.exists(key):
                raise APIException(f'Key "{key}" 不存在', 404)
            
            # 获取 key 类型
            key_type_raw = client.type(key)
            key_type = key_type_raw.decode('utf-8') if isinstance(key_type_raw, bytes) else str(key_type_raw)
            
            # 获取 TTL
            ttl = client.ttl(key)
            
            # 获取值（根据类型）
            value = None
            size = 0
            
            if key_type == 'string':
                value = client.get(key)
                size = len(value) if value else 0
            elif key_type == 'list':
                length = client.llen(key)
                value = client.lrange(key, 0, min(100, length - 1))  # 最多返回前100个元素
                size = length
            elif key_type == 'set':
                length = client.scard(key)
                value = list(client.smembers(key))[:100]  # 最多返回前100个元素
                size = length
            elif key_type == 'zset':
                length = client.zcard(key)
                value = client.zrange(key, 0, min(100, length - 1), withscores=True)  # 最多返回前100个元素
                size = length
            elif key_type == 'hash':
                length = client.hlen(key)
                value = client.hgetall(key)
                size = length
            elif key_type == 'stream':
                length = client.xlen(key)
                value = client.xrange(key, count=100)  # 最多返回前100个消息
                size = length
            
            # 格式化值用于显示
            formatted_value = self._format_value(value, key_type)
            
            # 确保 raw_value 也是可序列化的（格式化为可序列化格式）
            raw_value_formatted = self._format_value(value, key_type)
            
            return {
                'key': key,
                'type': key_type,
                'ttl': ttl,
                'size': size,
                'value': formatted_value,
                'raw_value': raw_value_formatted
            }
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'获取 key 信息失败: {str(e)}', 500)
    
    def _format_value(self, value, key_type: str):
        """格式化值用于显示"""
        if value is None:
            return None
        
        try:
            if key_type == 'string':
                # 尝试解码为字符串
                if isinstance(value, bytes):
                    try:
                        return value.decode('utf-8')
                    except UnicodeDecodeError:
                        return value.hex()  # 如果是二进制数据，返回十六进制
                return str(value)
            
            elif key_type == 'list':
                return [item.decode('utf-8') if isinstance(item, bytes) else str(item) for item in value]
            
            elif key_type == 'set':
                return [item.decode('utf-8') if isinstance(item, bytes) else str(item) for item in value]
            
            elif key_type == 'zset':
                return [(item[0].decode('utf-8') if isinstance(item[0], bytes) else str(item[0]), item[1]) for item in value]
            
            elif key_type == 'hash':
                result = {}
                for k, v in value.items():
                    key_str = k.decode('utf-8') if isinstance(k, bytes) else str(k)
                    val_str = v.decode('utf-8') if isinstance(v, bytes) else str(v)
                    result[key_str] = val_str
                return result
            
            elif key_type == 'stream':
                return [{
                    'id': msg[0].decode('utf-8') if isinstance(msg[0], bytes) else str(msg[0]),
                    'fields': {k.decode('utf-8') if isinstance(k, bytes) else str(k): 
                              v.decode('utf-8') if isinstance(v, bytes) else str(v) 
                              for k, v in msg[1].items()}
                } for msg in value]
            
            return str(value)
        except Exception as e:
            return f"格式化错误: {str(e)}"
    
    def set_key_value(self, connection_id, key: str, value: str, key_type: str = 'string', ttl: Optional[int] = None, **kwargs):
        """设置 key 的值"""
        try:
            client = self._get_redis_client(connection_id)
            
            if key_type == 'string':
                client.set(key, value)
                if ttl and ttl > 0:
                    client.expire(key, ttl)
            
            elif key_type == 'list':
                # kwargs 可能包含: operation (append/prepend), index (for insert)
                operation = kwargs.get('operation', 'append')
                if operation == 'append':
                    client.rpush(key, value)
                elif operation == 'prepend':
                    client.lpush(key, value)
                if ttl and ttl > 0:
                    client.expire(key, ttl)
            
            elif key_type == 'set':
                client.sadd(key, value)
                if ttl and ttl > 0:
                    client.expire(key, ttl)
            
            elif key_type == 'zset':
                score = kwargs.get('score', 0)
                client.zadd(key, {value: score})
                if ttl and ttl > 0:
                    client.expire(key, ttl)
            
            elif key_type == 'hash':
                field = kwargs.get('field')
                if not field:
                    raise APIException('Hash 类型需要提供 field 参数', 400)
                client.hset(key, field, value)
                if ttl and ttl > 0:
                    client.expire(key, ttl)
            
            else:
                raise APIException(f'不支持的类型: {key_type}', 400)
            
            return {'success': True, 'message': '设置成功'}
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'设置 key 失败: {str(e)}', 500)
    
    def delete_key(self, connection_id, key: str):
        """删除 key"""
        try:
            client = self._get_redis_client(connection_id)
            
            if not client.exists(key):
                raise APIException(f'Key "{key}" 不存在', 404)
            
            deleted = client.delete(key)
            
            return {
                'success': True,
                'message': f'删除成功，共删除 {deleted} 个 key',
                'deleted_count': deleted
            }
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'删除 key 失败: {str(e)}', 500)
    
    def delete_keys(self, connection_id, keys: List[str]):
        """批量删除 keys"""
        try:
            client = self._get_redis_client(connection_id)
            
            if not keys:
                raise APIException('请提供要删除的 keys', 400)
            
            deleted = client.delete(*keys)
            
            return {
                'success': True,
                'message': f'删除成功，共删除 {deleted} 个 key',
                'deleted_count': deleted
            }
        except Exception as e:
            raise APIException(f'批量删除 keys 失败: {str(e)}', 500)
    
    def update_key_value(self, connection_id, key: str, value: str, key_type: str = None, ttl: Optional[int] = None, **kwargs):
        """更新 key 的值"""
        try:
            client = self._get_redis_client(connection_id)
            
            if not client.exists(key):
                raise APIException(f'Key "{key}" 不存在', 404)
            
            # 如果没有指定类型，自动检测
            if not key_type:
                key_type = client.type(key).decode('utf-8') if isinstance(client.type(key), bytes) else client.type(key)
            
            # 根据类型更新
            if key_type == 'string':
                client.set(key, value)
                if ttl and ttl > 0:
                    client.expire(key, ttl)
                elif ttl == -1:
                    client.persist(key)  # 移除过期时间
            
            elif key_type == 'hash':
                field = kwargs.get('field')
                if not field:
                    raise APIException('Hash 类型需要提供 field 参数', 400)
                client.hset(key, field, value)
                if ttl and ttl > 0:
                    client.expire(key, ttl)
            
            else:
                # 对于其他类型，先删除再创建
                client.delete(key)
                return self.set_key_value(connection_id, key, value, key_type, ttl, **kwargs)
            
            return {'success': True, 'message': '更新成功'}
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'更新 key 失败: {str(e)}', 500)
    
    def get_key_count(self, connection_id, pattern='*'):
        """获取 key 的数量（估算）"""
        try:
            client = self._get_redis_client(connection_id)
            
            # 使用 DBSIZE 获取总 key 数（如果 pattern 是 *）
            if pattern == '*':
                count = client.dbsize()
            else:
                # 对于特定 pattern，使用 SCAN 估算
                count = 0
                cursor = 0
                while True:
                    cursor_result = client.scan(cursor=cursor, match=pattern, count=1000)
                    cursor, keys = cursor_result
                    count += len(keys)
                    if cursor == 0:
                        break
            
            return {'count': count}
        except Exception as e:
            raise APIException(f'获取 key 数量失败: {str(e)}', 500)
    
    def execute_command(self, connection_id, command: str):
        """执行 Redis 命令"""
        try:
            client = self._get_redis_client(connection_id)
            
            # 解析命令（简单的命令解析，支持基本格式）
            parts = command.strip().split()
            if not parts:
                raise APIException('命令不能为空', 400)
            
            cmd = parts[0].upper()
            args = parts[1:] if len(parts) > 1 else []
            
            # 安全检查：禁止执行危险命令
            dangerous_commands = ['FLUSHALL', 'FLUSHDB', 'CONFIG', 'SHUTDOWN', 'DEBUG', 'SAVE', 'BGSAVE']
            if cmd in dangerous_commands:
                raise APIException(f'出于安全考虑，不允许执行 {cmd} 命令', 403)
            
            # 执行命令
            result = client.execute_command(cmd, *args)
            
            # 格式化结果（确保所有数据都是可序列化的）
            formatted_result = self._format_command_result(result)
            
            return {
                'success': True,
                'command': command,
                'result': formatted_result
            }
        except APIException:
            raise
        except Exception as e:
            raise APIException(f'执行命令失败: {str(e)}', 500)
    
    def _format_command_result(self, result):
        """格式化命令执行结果"""
        if result is None:
            return None
        
        # 如果是 bytes，尝试解码
        if isinstance(result, bytes):
            try:
                return result.decode('utf-8')
            except UnicodeDecodeError:
                return result.hex()
        
        # 如果是列表，递归处理每个元素
        if isinstance(result, list):
            return [self._format_command_result(item) for item in result]
        
        # 如果是字典，递归处理每个键和值
        if isinstance(result, dict):
            formatted_dict = {}
            for k, v in result.items():
                # 格式化键（如果是 bytes）
                if isinstance(k, bytes):
                    try:
                        key_str = k.decode('utf-8')
                    except UnicodeDecodeError:
                        key_str = k.hex()
                else:
                    key_str = str(k)
                # 格式化值
                formatted_dict[key_str] = self._format_command_result(v)
            return formatted_dict
        
        # 如果是元组，转换为列表
        if isinstance(result, tuple):
            return [self._format_command_result(item) for item in result]
        
        return result
    
    def close_connection(self, connection_id):
        """关闭 Redis 连接"""
        connection_key = self._get_connection_key(connection_id)
        if connection_key in self.connection_pool:
            try:
                client = self.connection_pool[connection_key]
                client.close()
            except Exception:
                pass
            finally:
                del self.connection_pool[connection_key]
        
        return {'message': '连接已关闭'}

