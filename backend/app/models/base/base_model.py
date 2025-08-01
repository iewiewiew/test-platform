#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  基础模型类 - 提供所有数据模型的通用功能
"""

from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history
from sqlalchemy.orm import declared_attr

from ...core.database import db, datetime, tz_beijing


class BaseModel(db.Model):
    """抽象基础模型类，所有数据模型的基类"""
    __abstract__ = True

    # 基础字段 - id 必须在第一列
    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    
    # 标准字段（将在表创建时添加到末尾）
    # 这些字段通过 @declared_attr 延迟定义，确保在子类字段之后
    @declared_attr
    def is_active(cls):
        return db.Column(db.Boolean, default=True, nullable=False, comment='是否激活')
    
    @declared_attr
    def created_by(cls):
        return db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='创建人ID')
    
    @declared_attr
    def updated_by(cls):
        return db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='最后更新人ID')
    
    @declared_attr
    def created_at(cls):
        return db.Column(db.DateTime, default=lambda: datetime.now(tz_beijing), nullable=False, comment='创建时间')
    
    @declared_attr
    def updated_at(cls):
        return db.Column(db.DateTime, default=lambda: datetime.now(tz_beijing), onupdate=lambda: datetime.now(tz_beijing), nullable=False, comment='更新时间')

    # 关联关系 - 使用@declared_attr装饰器，因为这是抽象基类
    @declared_attr
    def creator(cls):
        return db.relationship('User', foreign_keys=[cls.created_by], lazy='select', uselist=False)
    
    @declared_attr
    def updater(cls):
        return db.relationship('User', foreign_keys=[cls.updated_by], lazy='select', uselist=False)

    def to_dict(self, exclude_fields=None, include_relationships=False, max_depth=1):
        """
        将模型实例转换为字典

        Args:
            exclude_fields: 要排除的字段列表
            include_relationships: 是否包含关联关系
            max_depth: 关联关系最大深度（防止循环引用）

        Returns:
            dict: 模型数据的字典表示
        """
        if exclude_fields is None:
            exclude_fields = ['_sa_instance_state']

        result = {}

        # 处理列字段
        for column in self.__table__.columns:
            if column.name in exclude_fields:
                continue

            value = getattr(self, column.name)
            result[column.name] = self._serialize_value(value)

        # 添加创建人和更新人名称（如果存在）
        if hasattr(self, 'creator') and self.creator:
            result['creator_name'] = self.creator.username
        if hasattr(self, 'updater') and self.updater:
            result['updater_name'] = self.updater.username

        # 处理关联关系
        if include_relationships and max_depth > 0:
            for relationship in self.__mapper__.relationships:
                if relationship.key in exclude_fields:
                    continue

                related_objects = getattr(self, relationship.key)
                if related_objects is None:
                    result[relationship.key] = None
                elif isinstance(related_objects, list):
                    result[relationship.key] = [
                        obj.to_dict(include_relationships=False) if hasattr(obj, 'to_dict') else self._serialize_value(
                            obj) for obj in related_objects]
                else:
                    if hasattr(related_objects, 'to_dict'):
                        result[relationship.key] = related_objects.to_dict(include_relationships=True,
                            max_depth=max_depth - 1)
                    else:
                        result[relationship.key] = self._serialize_value(related_objects)

        return result

    def _serialize_value(self, value):
        """序列化特殊类型的值"""
        if value is None:
            return None
        elif isinstance(value, datetime):
            return value.isoformat()
        elif hasattr(value, 'isoformat'):  # 处理其他日期时间类型
            return value.isoformat()
        elif hasattr(value, '__table__'):  # 如果是模型实例
            return {'id': value.id, '__class__': value.__class__.__name__}
        else:
            return value

    @classmethod
    def get_by_id(cls, id):
        """根据ID获取实例"""
        return cls.query.get(id)

    @classmethod
    def get_all_active(cls):
        """获取所有激活的实例"""
        return cls.query.filter_by(is_active=True).all()

    @classmethod
    def create(cls, **kwargs):
        """创建新实例"""
        instance = cls(**kwargs)
        db.session.add(instance)
        return instance

    def update(self, **kwargs):
        """更新实例字段"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(tz_beijing)

    def save(self):
        """保存实例到数据库"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            # 在实际项目中，这里应该使用日志记录
            print(f"保存失败: {e}")
            return False

    def delete(self, soft_delete=True):
        """
        删除实例

        Args:
            soft_delete: 是否软删除（默认True）
        """
        try:
            if soft_delete and hasattr(self, 'is_active'):
                self.is_active = False
                db.session.commit()
            else:
                db.session.delete(self)
                db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"删除失败: {e}")
            return False

    def refresh(self):
        """从数据库重新加载实例"""
        db.session.refresh(self)

    def get_changes(self):
        """获取未提交的更改"""
        changes = {}
        for attr in self.__table__.columns.keys():
            history = get_history(self, attr)
            if history.has_changes():
                changes[attr] = {'old': list(history.deleted), 'new': list(history.added)}
        return changes

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'

    def __str__(self):
        return f'{self.__class__.__name__}(id={self.id})'


# 添加时间戳自动更新的事件监听器
@event.listens_for(BaseModel, 'before_update', propagate=True)
def update_updated_at(mapper, connection, target):
    """在更新前自动更新 updated_at 字段"""
    target.updated_at = datetime.now(tz_beijing)
