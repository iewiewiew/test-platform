#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  常用文档服务类
"""

import os
from pathlib import Path
import re


class DocsService:
    """文档服务类"""

    @staticmethod
    def get_docs_dir():
        """获取文档目录路径"""
        # 获取项目根目录
        current_file = Path(__file__).resolve()  # 使用绝对路径
        # backend/app/services/api_docs/docs_service.py -> backend/app/docs
        docs_dir = current_file.parent.parent.parent / 'docs'
        return docs_dir

    @staticmethod
    def get_doc_name_from_file(file_name):
        """从文件名获取文档名称（去掉 .md 后缀）"""
        if file_name.endswith('.md'):
            return file_name[:-3]
        return file_name

    @staticmethod
    def get_file_name_from_doc_name(doc_name):
        """从文档名称获取文件名（添加 .md 后缀）"""
        if not doc_name.endswith('.md'):
            return f'{doc_name}.md'
        return doc_name

    @staticmethod
    def validate_doc_name(doc_name):
        """验证文档名称是否合法"""
        if not doc_name or not doc_name.strip():
            return False, '文档名称不能为空'
        
        # 去除首尾空格
        doc_name = doc_name.strip()
        
        # 检查是否包含非法字符（只允许字母、数字、下划线、中划线、中文）
        if not re.match(r'^[\w\-\u4e00-\u9fa5]+$', doc_name):
            return False, '文档名称只能包含字母、数字、下划线、中划线和中文'
        
        # 检查长度
        if len(doc_name) > 100:
            return False, '文档名称长度不能超过100个字符'
        
        return True, doc_name

    @staticmethod
    def get_doc(doc_path):
        """获取指定路径的文档内容（支持子目录路径，如：subdir/doc.md 或 doc.md）"""
        try:
            docs_dir = DocsService.get_docs_dir()
            
            # 处理路径，确保安全（防止路径遍历攻击）
            if '..' in doc_path or doc_path.startswith('/'):
                return {'code': 1, 'message': '无效的文档路径'}
            
            # 如果路径不包含 .md 后缀，自动添加
            if not doc_path.endswith('.md'):
                # 检查是否是目录路径
                test_path = docs_dir / doc_path
                if test_path.exists() and test_path.is_dir():
                    return {'code': 1, 'message': '路径指向目录，不是文件'}
                doc_path = DocsService.get_file_name_from_doc_name(doc_path)
            
            file_path = docs_dir / doc_path

            if not file_path.exists():
                return {'code': 1, 'message': f'文档文件不存在: {doc_path}'}
            
            # 确保文件在 docs 目录内（防止路径遍历）
            try:
                file_path.resolve().relative_to(docs_dir.resolve())
            except ValueError:
                return {'code': 1, 'message': '无效的文档路径'}

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 获取文档名称（去掉路径和扩展名）
            doc_name = file_path.stem
            if '/' in doc_path:
                path_parts = Path(doc_path).parts
                if len(path_parts) > 1:
                    doc_name = f"{'/'.join(path_parts[:-1])}/{doc_name}"

            return {
                'code': 0,
                'message': 'success',
                'data': {
                    'name': doc_name,
                    'title': doc_name,
                    'path': doc_path,
                    'content': content
                }
            }
        except Exception as e:
            return {'code': 1, 'message': f'读取文档失败: {str(e)}'}

    @staticmethod
    def build_tree_structure(docs_dir, relative_path=''):
        """递归构建目录树结构"""
        tree = []
        current_dir = docs_dir / relative_path if relative_path else docs_dir
        
        if not current_dir.exists() or not current_dir.is_dir():
            return tree
        
        items = []
        # 收集所有文件和目录
        for item in sorted(current_dir.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            # 跳过隐藏文件
            if item.name.startswith('.'):
                continue
            
            if item.is_dir():
                # 递归处理子目录
                sub_path = f"{relative_path}/{item.name}" if relative_path else item.name
                children = DocsService.build_tree_structure(docs_dir, sub_path)
                items.append({
                    'name': item.name,
                    'title': item.name,
                    'type': 'directory',
                    'path': sub_path,
                    'children': children
                })
            elif item.is_file():
                # 处理文件（包括 Markdown 文件和图片文件）
                file_name = item.name
                file_path = f"{relative_path}/{file_name}" if relative_path else file_name
                
                # 判断文件类型
                if item.suffix == '.md':
                    # Markdown 文件
                    doc_name = DocsService.get_doc_name_from_file(file_name)
                    items.append({
                        'name': doc_name,
                        'title': doc_name,
                        'type': 'file',
                        'path': file_path,
                        'file': file_name
                    })
                elif item.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'}:
                    # 图片文件
                    items.append({
                        'name': file_name,
                        'title': file_name,
                        'type': 'image',
                        'path': file_path,
                        'file': file_name
                    })
        
        return items

    @staticmethod
    def get_docs_list():
        """获取所有可用文档列表（递归读取目录结构，返回树形数据）"""
        try:
            docs_dir = DocsService.get_docs_dir()

            # 确保目录存在
            if not docs_dir.exists():
                docs_dir.mkdir(parents=True, exist_ok=True)
                return {
                    'code': 0,
                    'message': 'success',
                    'data': []
                }

            # 构建目录树
            tree_data = DocsService.build_tree_structure(docs_dir)

            return {
                'code': 0,
                'message': 'success',
                'data': tree_data
            }
        except Exception as e:
            import traceback
            error_msg = f'获取文档列表失败: {str(e)}\n{traceback.format_exc()}'
            print(f"Error in get_docs_list: {error_msg}")
            return {'code': 1, 'message': f'获取文档列表失败: {str(e)}'}

    @staticmethod
    def create_doc(doc_path, content=''):
        """创建新文档（支持子目录路径，如：subdir/doc.md）"""
        try:
            docs_dir = DocsService.get_docs_dir()
            
            # 处理路径，确保安全
            if '..' in doc_path or doc_path.startswith('/'):
                return {'code': 1, 'message': '无效的文档路径'}
            
            # 如果路径不包含 .md 后缀，自动添加
            if not doc_path.endswith('.md'):
                doc_path = DocsService.get_file_name_from_doc_name(doc_path)
            
            file_path = docs_dir / doc_path
            
            # 确保父目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 确保文件在 docs 目录内
            try:
                file_path.resolve().relative_to(docs_dir.resolve())
            except ValueError:
                return {'code': 1, 'message': '无效的文档路径'}

            # 检查文件是否已存在
            if file_path.exists():
                return {'code': 1, 'message': f'文档已存在: {doc_path}'}

            # 创建文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # 获取文档名称
            doc_name = file_path.stem
            if '/' in doc_path:
                doc_name = f"{Path(doc_path).parent.name}/{doc_name}"

            return {
                'code': 0,
                'message': 'success',
                'data': {
                    'name': doc_name,
                    'title': doc_name,
                    'path': doc_path,
                    'file': Path(doc_path).name
                }
            }
        except Exception as e:
            return {'code': 1, 'message': f'创建文档失败: {str(e)}'}

    @staticmethod
    def update_doc(doc_path, content):
        """更新文档内容（支持子目录路径）"""
        try:
            docs_dir = DocsService.get_docs_dir()
            
            # 处理路径，确保安全
            if '..' in doc_path or doc_path.startswith('/'):
                return {'code': 1, 'message': '无效的文档路径'}
            
            # 如果路径不包含 .md 后缀，自动添加
            if not doc_path.endswith('.md'):
                doc_path = DocsService.get_file_name_from_doc_name(doc_path)
            
            file_path = docs_dir / doc_path
            
            # 确保文件在 docs 目录内
            try:
                file_path.resolve().relative_to(docs_dir.resolve())
            except ValueError:
                return {'code': 1, 'message': '无效的文档路径'}

            # 检查文件是否存在
            if not file_path.exists():
                return {'code': 1, 'message': f'文档文件不存在: {doc_path}'}

            # 更新文件内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # 获取文档名称
            doc_name = file_path.stem
            if '/' in doc_path:
                doc_name = f"{Path(doc_path).parent.name}/{doc_name}"

            return {
                'code': 0,
                'message': 'success',
                'data': {
                    'name': doc_name,
                    'title': doc_name,
                    'path': doc_path
                }
            }
        except Exception as e:
            return {'code': 1, 'message': f'更新文档失败: {str(e)}'}

    @staticmethod
    def delete_doc(doc_path):
        """删除文档或图片文件（支持子目录路径）"""
        try:
            docs_dir = DocsService.get_docs_dir()
            
            # 处理路径，确保安全
            if '..' in doc_path or doc_path.startswith('/'):
                return {'code': 1, 'message': '无效的文档路径'}
            
            # 检查是否是图片文件
            is_image = any(doc_path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'])
            
            # 如果不是图片文件，且路径不包含 .md 后缀，自动添加
            if not is_image and not doc_path.endswith('.md'):
                doc_path = DocsService.get_file_name_from_doc_name(doc_path)
            
            file_path = docs_dir / doc_path
            
            # 确保文件在 docs 目录内
            try:
                file_path.resolve().relative_to(docs_dir.resolve())
            except ValueError:
                return {'code': 1, 'message': '无效的文档路径'}

            # 检查文件是否存在
            if not file_path.exists():
                return {'code': 1, 'message': f'文件不存在: {doc_path}'}

            # 删除文件
            file_path.unlink()

            return {
                'code': 0,
                'message': 'success'
            }
        except Exception as e:
            return {'code': 1, 'message': f'删除文件失败: {str(e)}'}

