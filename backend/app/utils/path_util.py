#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author      weimenghua
@time        2020/8/24 21:54
@description 路径工具类
"""

import os
from os.path import dirname, join, normpath
from pathlib import Path


class PathUtils:
    @staticmethod
    def get_current_file_path():
        """获取当前文件的绝对路径

        Returns:
            str: 当前文件的绝对路径
        """
        return os.path.realpath(__file__)

    @staticmethod
    def get_current_dir_path():
        """获取当前文件所在目录的绝对路径

        Returns:
            str: 当前目录的绝对路径
        """
        return os.path.abspath(dirname(__file__))

    @staticmethod
    def get_parent_dir_path(levels=1):
        """获取指定层级的上级目录路径

        Args:
            levels (int): 向上追溯的目录层级数（默认为1）

        Returns:
            str: 上级目录的绝对路径

        Raises:
            ValueError: 如果levels为负数
        """
        if levels < 0:
            raise ValueError("层级数必须是非负整数")

        current_dir = PathUtils.get_current_dir_path()
        for _ in range(levels):
            current_dir = dirname(current_dir)
        return normpath(current_dir)  # 规范化路径格式

    @staticmethod
    def get_project_root_path(project_name):
        """获取项目根目录的绝对路径

        Args:
            project_name (str): 项目名称（用于在路径中查找）

        Returns:
            str: 项目根目录的绝对路径

        Raises:
            ValueError: 如果在路径中找不到项目名称，且不在 Docker 环境中
        """
        current_path = PathUtils.get_current_dir_path()
        
        # 首先尝试查找项目名称（兼容本地开发环境）
        search_pattern = f"{project_name}{os.sep}"  # 使用系统分隔符
        index = current_path.find(search_pattern)

        if index != -1:
            return normpath(current_path[:index + len(search_pattern)])
        
        # 如果在 Docker 环境中（路径以 /app 开头），直接返回 /app
        # 或者基于当前文件位置向上查找，直到找到包含 backend 目录的路径
        if current_path.startswith('/app'):
            # Docker 环境：/app 就是项目根目录（backend 目录被挂载到 /app）
            return '/app'
        
        # 尝试向上查找，直到找到包含 backend 目录的路径
        # 这样可以兼容不同的部署环境
        path_obj = Path(current_path)
        for parent in path_obj.parents:
            backend_dir = parent / 'backend'
            if backend_dir.exists() and backend_dir.is_dir():
                # 如果找到了 backend 目录，返回其父目录（项目根目录）
                return str(parent)
        
        # 如果都找不到，尝试使用环境变量或配置
        # 检查是否有 PROJECT_ROOT 环境变量
        project_root = os.environ.get('PROJECT_ROOT')
        if project_root and os.path.exists(project_root):
            return project_root
        
        # 最后尝试：如果当前路径包含 'app' 目录，假设上一级是项目根目录
        if 'app' in current_path:
            app_index = current_path.rfind(os.sep + 'app' + os.sep)
            if app_index != -1:
                # 找到 app 目录，返回上一级（backend 目录）
                backend_path = current_path[:app_index + len(os.sep + 'app')]
                # 如果 backend_path 以 backend/app 结尾，返回 backend 的父目录
                if backend_path.endswith(os.sep + 'backend' + os.sep + 'app'):
                    return str(Path(backend_path).parent.parent)
                return str(Path(backend_path).parent)
        
        # 如果所有方法都失败，抛出异常
        raise ValueError(f"在路径中找不到项目名称: '{project_name}'。当前路径: {current_path}")

    @staticmethod
    def get_file_path(project_name, *path_components):
        """构建基于项目根目录的绝对路径

        Args:
            project_name (str): 项目名称
            *path_components: 要拼接的路径组成部分（可变参数）

        Returns:
            str: 由项目根目录和路径部分组成的绝对路径
        """
        project_root = PathUtils.get_project_root_path(project_name)
        
        # 在 Docker 环境中，如果 project_root 是 /app，且路径组件以 'backend' 开头，则跳过 'backend'
        # 因为 /app 本身就是 backend 目录的内容
        if project_root == '/app' and path_components and path_components[0] == 'backend':
            path_components = path_components[1:]  # 跳过 'backend' 组件
        
        return normpath(join(project_root, *path_components))  # 拼接并规范化路径

    @staticmethod
    def get_os_sep():
        """获取当前操作系统的路径分隔符

        Returns:
            str: 操作系统路径分隔符（Windows为"\", Unix为"/"）
        """
        return os.sep

    @staticmethod
    def get_user_home_path():
        """获取当前用户的主目录路径

        Returns:
            str: 用户主目录的绝对路径
        """
        return os.path.expanduser("~")  # 跨平台获取用户主目录


if __name__ == "__main__":
    # 工具类使用示例
    print("当前文件路径:", PathUtils.get_current_file_path())
    print("当前目录路径:", PathUtils.get_current_dir_path())
    print("上级目录(1层):", PathUtils.get_parent_dir_path())
    print("上级目录(2层):", PathUtils.get_parent_dir_path(2))

    try:
        project_name = "Learn-Python"
        print(f"项目'{project_name}'根路径:",
              PathUtils.get_project_root_path(project_name))
        print("项目内文件路径:",
              PathUtils.get_file_path(project_name, "files"))
    except ValueError as e:
        print(f"错误: {e}")

    print("系统路径分隔符:", PathUtils.get_os_sep())
    print("用户主目录:", PathUtils.get_user_home_path())