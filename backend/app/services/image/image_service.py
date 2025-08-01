#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/12/22
@description  图片业务逻辑服务层
"""

import os
from PIL import Image as PILImage
from werkzeug.utils import secure_filename
from flask import current_app

from ...core.database import db
from ...models.image.image_model import Image


class ImageService:
    """图片业务服务类"""

    @staticmethod
    def allowed_file(filename):
        """检查文件扩展名是否允许"""
        allowed_extensions = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
        if '.' not in filename:
            return False
        try:
            ext = filename.rsplit('.', 1)[1].lower()
            return ext in allowed_extensions
        except IndexError:
            return False

    @staticmethod
    def get_all_images(page=1, per_page=10, filename=None):
        """
        获取所有图片记录（支持分页和条件筛选）

        Args:
            page (int): 页码，默认为 1
            per_page (int): 每页记录数，默认为 10
            filename (str, optional): 按文件名模糊筛选

        Returns:
            dict: 包含数据列表和总数的字典
        """
        query = Image.query.filter_by(is_active=True)

        if filename:
            query = query.filter(Image.filename.ilike(f'%{filename}%'))

        pagination = query.order_by(Image.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'data': [image.to_dict() for image in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }

    @staticmethod
    def get_image_by_id(image_id):
        """
        根据 ID 获取单个图片记录

        Args:
            image_id (int): 图片记录的主键 ID

        Returns:
            Image: 查询到的 Image 对象，如果不存在则返回 None
        """
        return Image.query.filter_by(id=image_id, is_active=True).first()

    @staticmethod
    def generate_unique_filename(base_filename, upload_folder, exclude_image_id=None):
        """
        生成唯一文件名，如果文件名已存在则添加 -1、-2 等后缀

        Args:
            base_filename (str): 基础文件名（已通过 secure_filename 处理）
            upload_folder (str): 上传文件夹路径
            exclude_image_id (int, optional): 排除的图片ID（用于更新时排除当前图片）

        Returns:
            str: 唯一的文件名
        """
        # 检查文件名是否已存在（数据库和文件系统）
        def filename_exists(filename):
            # 检查数据库中是否存在
            query = Image.query.filter_by(filename=filename, is_active=True)
            if exclude_image_id:
                query = query.filter(Image.id != exclude_image_id)
            if query.first():
                return True
            
            # 检查文件系统中是否存在
            file_path = os.path.join(upload_folder, filename)
            return os.path.exists(file_path)

        # 如果基础文件名不存在，直接返回
        if not filename_exists(base_filename):
            return base_filename

        # 分离文件名和扩展名
        if '.' in base_filename:
            name_part, ext_part = base_filename.rsplit('.', 1)
        else:
            name_part = base_filename
            ext_part = ''

        # 尝试添加 -1、-2 等后缀
        counter = 1
        while True:
            if ext_part:
                new_filename = f"{name_part}-{counter}.{ext_part}"
            else:
                new_filename = f"{name_part}-{counter}"
            
            if not filename_exists(new_filename):
                return new_filename
            
            counter += 1
            
            # 防止无限循环（理论上不会发生，但安全起见）
            if counter > 10000:
                raise ValueError('无法生成唯一文件名，请重试')

    @staticmethod
    def upload_image(file, description=None, current_user=None):
        """
        上传图片

        Args:
            file: 上传的文件对象
            description (str, optional): 图片描述
            current_user: 当前用户对象

        Returns:
            Image: 新创建的 Image 对象

        Raises:
            ValueError: 文件格式不支持或文件过大
        """
        if not file or not file.filename:
            raise ValueError('未选择文件')

        if not ImageService.allowed_file(file.filename):
            raise ValueError('不支持的文件格式')

        # 获取配置
        upload_folder = current_app.config.get('IMAGE_UPLOAD_FOLDER')
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)

        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > max_size:
            raise ValueError(f'文件大小超过限制（最大 {max_size // 1024 // 1024}MB）')

        # 确保上传目录存在
        os.makedirs(upload_folder, exist_ok=True)

        # 处理文件名：保持原始文件名，重复时添加 -1、-2 等后缀
        original_filename = secure_filename(file.filename)
        
        # 安全地获取文件扩展名
        # 先尝试从处理后的文件名获取，如果失败则从原始文件名获取
        file_ext = None
        for filename_to_check in [original_filename, file.filename]:
            if '.' in filename_to_check:
                parts = filename_to_check.rsplit('.', 1)
                if len(parts) == 2 and parts[1]:
                    file_ext = parts[1].lower()
                    break
        
        if not file_ext:
            raise ValueError(f'无法从文件名中提取扩展名: {file.filename}')
        
        # 验证扩展名是否在允许列表中（双重检查，确保安全）
        allowed_extensions = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
        if file_ext not in allowed_extensions:
            raise ValueError(f'不支持的文件扩展名: {file_ext}')
        
        # 生成唯一文件名（保持原始文件名，重复时添加后缀）
        unique_filename = ImageService.generate_unique_filename(original_filename, upload_folder)

        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # 获取图片信息
        width = None
        height = None
        mime_type = file.content_type or f'image/{file_ext}'

        try:
            with PILImage.open(file_path) as img:
                width, height = img.size
        except Exception:
            pass

        # 生成访问URL（使用API路由，支持直接访问）
        url = f"/api/images/{unique_filename}"

        # 创建数据库记录
        image = Image(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            width=width,
            height=height,
            description=description,
            url=url
        )

        if current_user:
            image.created_by = current_user.id
            image.updated_by = current_user.id

        db.session.add(image)
        db.session.commit()

        return image

    @staticmethod
    def update_image(image_id, data, file=None, current_user=None):
        """
        更新图片信息（支持更新图片文件，但保留原有文件名）

        Args:
            image_id (int): 要更新的图片记录 ID
            data (dict): 包含要更新字段的字典
                - description (str, optional): 新描述
            file (file object, optional): 新的图片文件（如果提供，将替换原文件但保留原文件名）
            current_user: 当前用户对象

        Returns:
            Image or None: 更新后的 Image 对象，如果记录不存在则返回 None

        Raises:
            ValueError: 文件格式不支持或文件过大
        """
        image = Image.query.filter_by(id=image_id, is_active=True).first()
        if not image:
            return None

        # 如果提供了新文件，更新文件但保留原有文件名
        if file and file.filename:
            # 验证文件格式
            if not ImageService.allowed_file(file.filename):
                raise ValueError('不支持的文件格式')

            # 获取配置
            upload_folder = current_app.config.get('IMAGE_UPLOAD_FOLDER')
            max_size = current_app.config.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)

            # 检查文件大小
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > max_size:
                raise ValueError(f'文件大小超过限制（最大 {max_size // 1024 // 1024}MB）')

            # 保留原有的文件名（filename），只更新文件内容
            original_filename = secure_filename(file.filename)
            
            # 安全地获取新文件的扩展名
            file_ext = None
            for filename_to_check in [original_filename, file.filename]:
                if '.' in filename_to_check:
                    parts = filename_to_check.rsplit('.', 1)
                    if len(parts) == 2 and parts[1]:
                        file_ext = parts[1].lower()
                        break

            if not file_ext:
                raise ValueError(f'无法从文件名中提取扩展名: {file.filename}')

            # 验证扩展名
            allowed_extensions = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
            if file_ext not in allowed_extensions:
                raise ValueError(f'不支持的文件扩展名: {file_ext}')

            # 保留原有的文件名（filename 不变）
            old_filename = image.filename
            new_filename = old_filename  # 保持原文件名不变

            # 确保上传目录存在
            os.makedirs(upload_folder, exist_ok=True)

            # 删除旧文件（如果存在）
            old_file_path = image.file_path
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except Exception:
                    pass  # 忽略删除失败

            # 保存新文件（使用保留的文件名）
            new_file_path = os.path.join(upload_folder, new_filename)
            file.save(new_file_path)

            # 获取新图片信息
            width = None
            height = None
            mime_type = file.content_type or f'image/{file_ext}'

            try:
                with PILImage.open(new_file_path) as img:
                    width, height = img.size
            except Exception:
                pass

            # 更新文件相关字段（文件名和URL保持不变）
            image.original_filename = original_filename  # 更新原始文件名为新上传的文件名
            image.file_path = new_file_path
            image.file_size = file_size
            image.mime_type = mime_type
            image.width = width
            image.height = height
            # filename 和 url 保持不变，确保访问URL不变

        # 更新描述
        if 'description' in data:
            image.description = data['description']

        if current_user:
            image.updated_by = current_user.id

        db.session.commit()
        return image

    @staticmethod
    def delete_image(image_id):
        """
        删除图片（软删除）

        Args:
            image_id (int): 要删除的图片记录 ID

        Returns:
            bool: 删除成功返回 True，记录不存在返回 False
        """
        image = Image.query.filter_by(id=image_id, is_active=True).first()
        if not image:
            return False

        # 软删除
        image.is_active = False
        db.session.commit()

        # 可选：同时删除物理文件
        # if os.path.exists(image.file_path):
        #     os.remove(image.file_path)

        return True

    @staticmethod
    def batch_delete_images(image_ids):
        """
        批量删除图片

        Args:
            image_ids (list): 要删除的图片记录 ID 列表

        Returns:
            dict: 包含成功和失败统计的字典
        """
        success_count = 0
        failed_count = 0
        failed_ids = []

        for image_id in image_ids:
            try:
                image = Image.query.filter_by(id=image_id, is_active=True).first()
                if image:
                    image.is_active = False
                    success_count += 1
                else:
                    failed_count += 1
                    failed_ids.append(image_id)
            except Exception:
                failed_count += 1
                failed_ids.append(image_id)

        db.session.commit()

        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_ids': failed_ids
        }

