#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/12/22
@description  图片模型
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class Image(BaseModel):
    """图片模型"""
    __tablename__ = 'images'

    filename = db.Column(db.String(255), nullable=False, comment='文件名')
    original_filename = db.Column(db.String(255), nullable=False, comment='原始文件名')
    file_path = db.Column(db.String(500), nullable=False, comment='文件路径')
    file_size = db.Column(db.Integer, nullable=False, comment='文件大小（字节）')
    mime_type = db.Column(db.String(100), nullable=False, comment='MIME类型')
    width = db.Column(db.Integer, nullable=True, comment='图片宽度（像素）')
    height = db.Column(db.Integer, nullable=True, comment='图片高度（像素）')
    description = db.Column(db.Text, nullable=True, comment='描述')
    url = db.Column(db.String(500), nullable=False, comment='访问URL')

    def to_dict(self):
        """
        将图片对象转换为字典

        Returns:
            dict: 图片数据的字典表示
        """
        result = super().to_dict()
        return result

    def __repr__(self):
        return f'<Image {self.filename}>'

