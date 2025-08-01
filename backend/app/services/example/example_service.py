#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/21 10:04
@description  Example 业务逻辑服务层
              提供 Example 模型的 CRUD 操作及相关业务逻辑
"""

from ...core.database import db
from ...models.example.example_model import Example


class ExampleService:
    """Example 业务服务类，封装所有与 Example 相关的业务逻辑"""

    @staticmethod
    def get_all_examples(page=1, per_page=10, name=None, status=None):
        """
        获取所有 Example 记录（支持分页和条件筛选）

        Args:
            page (int): 页码，默认为 1
            per_page (int): 每页记录数，默认为 10
            name (str, optional): 按名称模糊筛选
            status (str, optional): 按状态精确筛选

        Returns:
            dict: 包含数据列表和总数的字典
                {
                    'data': [example_dict1, example_dict2, ...],
                    'total': 总记录数
                }
        """
        # 构建基础查询
        query = Example.query

        # 应用筛选条件
        if name:
            # 使用 ilike 进行不区分大小写的模糊匹配
            query = query.filter(Example.name.ilike(f'%{name}%'))
        if status:
            # 精确匹配状态
            query = query.filter(Example.status == status)

        # 执行分页查询，按ID降序排列
        pagination = query.order_by(Example.id.desc()).paginate(page=page, per_page=per_page, error_out=False
            # 页数超出范围时返回空列表而不是404
        )

        # 返回格式化结果
        return {'data': [example.to_dict() for example in pagination.items], 'total': pagination.total}

    @staticmethod
    def get_example_by_id(example_id):
        """
        根据 ID 获取单个 Example 记录

        Args:
            example_id (int): Example 记录的主键 ID

        Returns:
            Example: 查询到的 Example 对象，如果不存在则返回 None
        """
        example = Example.query.get(example_id)
        return example

    @staticmethod
    def create_example(data, current_user=None):
        """
        创建新的 Example 记录

        Args:
            data (dict): 包含 Example 字段数据的字典
                - name (str): 名称（必需）
                - description (str, optional): 描述信息
                - status (str, optional): 状态，默认为 'active'
            current_user: 当前用户对象

        Returns:
            Example: 新创建的 Example 对象

        Note:
            该方法会提交数据库事务
        """
        # 创建新的 Example 实例
        example = Example(name=data.get('name'), description=data.get('description'),
            status=data.get('status', 'active')  # 提供默认状态
        )
        if current_user:
            example.created_by = current_user.id
            example.updated_by = current_user.id

        # 保存到数据库
        db.session.add(example)
        db.session.commit()

        return example

    @staticmethod
    def update_example(example_id, data, current_user=None):
        """
        更新指定 ID 的 Example 记录

        Args:
            example_id (int): 要更新的 Example 记录 ID
            data (dict): 包含要更新字段的字典
                - name (str, optional): 新名称
                - description (str, optional): 新描述
                - status (str, optional): 新状态
            current_user: 当前用户对象

        Returns:
            Example or None: 更新后的 Example 对象，如果记录不存在则返回 None

        Note:
            只更新提供的字段，未提供的字段保持原值
        """
        # 查找要更新的记录
        example = Example.query.get(example_id)
        if not example:
            return None

        # 更新字段（如果提供了新值）
        example.name = data.get('name', example.name)  # 保持原值如果未提供
        example.description = data.get('description', example.description)
        example.status = data.get('status', example.status)
        
        if current_user:
            example.updated_by = current_user.id

        # 提交更新到数据库
        db.session.commit()

        return example

    @staticmethod
    def delete_example(example_id):
        """
        删除指定 ID 的 Example 记录

        Args:
            example_id (int): 要删除的 Example 记录 ID

        Returns:
            bool: 删除成功返回 True，记录不存在返回 False
        """
        # 查找要删除的记录
        example = Example.query.get(example_id)
        if not example:
            return False

        # 从数据库删除记录
        db.session.delete(example)
        db.session.commit()

        return True

    @staticmethod
    def batch_delete_examples(example_ids):
        """
        批量删除指定 ID 的 Example 记录

        Args:
            example_ids (list): 要删除的 Example 记录 ID 列表

        Returns:
            dict: 包含成功和失败统计的字典
                {
                    'success_count': 成功删除的数量,
                    'failed_count': 失败的数量,
                    'failed_ids': 失败记录的ID列表
                }
        """
        success_count = 0
        failed_count = 0
        failed_ids = []

        for example_id in example_ids:
            try:
                example = Example.query.get(example_id)
                if example:
                    db.session.delete(example)
                    success_count += 1
                else:
                    failed_count += 1
                    failed_ids.append(example_id)
            except Exception as e:
                failed_count += 1
                failed_ids.append(example_id)

        # 一次性提交所有删除操作
        db.session.commit()

        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_ids': failed_ids
        }