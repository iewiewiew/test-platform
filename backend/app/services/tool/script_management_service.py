#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/26
@description  自动化脚本管理服务层
"""

import os
import subprocess
import tempfile
import threading
import time
import json
from datetime import datetime, timezone, timedelta

from flask import current_app

from ...core.database import db
from ...core.exceptions import APIException
from ...models.tool.script_management_model import ScriptManagement, ScriptExecutionHistory

# 定时任务支持（可选，如果没有安装APScheduler则定时功能不可用）
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    print("警告: APScheduler未安装，定时任务功能将不可用。安装命令: pip install apscheduler")


tz_beijing = timezone(timedelta(hours=8))


class ScriptManagementService:
    """自动化脚本管理服务类"""
    
    def __init__(self):
        self.scheduler = None
        self.running_tasks = {}  # {execution_id: process}
        self.app = None  # Flask应用实例，用于在定时任务中创建应用上下文
        if APSCHEDULER_AVAILABLE:
            self.scheduler = BackgroundScheduler()
            self.scheduler.start()
            print("定时任务调度器已启动")
    
    def set_app(self, app):
        """设置Flask应用实例（用于定时任务执行时创建应用上下文）"""
        self.app = app
    
    def _execute_script_with_context(self, script_id, execution_type='scheduled', triggered_by='system'):
        """带应用上下文的脚本执行包装函数（用于定时任务）"""
        if not self.app:
            # 如果没有设置app，尝试从current_app获取
            try:
                self.app = current_app._get_current_object()
            except RuntimeError:
                print(f"错误: 无法获取Flask应用实例，定时任务 {script_id} 无法执行")
                return
        
        # 在应用上下文中执行脚本
        with self.app.app_context():
            try:
                self.execute_script(script_id, execution_type, triggered_by)
            except Exception as e:
                print(f"执行定时任务失败 (script_id={script_id}): {str(e)}")
                import traceback
                traceback.print_exc()
    
    def load_existing_scheduled_tasks(self):
        """从数据库加载所有已启用的定时任务"""
        if not APSCHEDULER_AVAILABLE or not self.scheduler:
            print("警告: APScheduler未安装或调度器未启动，无法加载定时任务")
            return
        
        try:
            # 查询所有已启用且设置了定时任务的脚本
            scripts = ScriptManagement.query.filter_by(
                is_active=True,
                is_enabled=True,
                is_scheduled=True
            ).filter(
                ScriptManagement.cron_expression.isnot(None),
                ScriptManagement.cron_expression != ''
            ).all()
            
            loaded_count = 0
            for script in scripts:
                try:
                    # 如果数据库中已有 job_id，先尝试从调度器中移除（可能不存在）
                    if script.schedule_job_id:
                        try:
                            self.scheduler.remove_job(script.schedule_job_id)
                        except:
                            pass  # 忽略不存在的任务
                    
                    # 重新调度任务
                    self._schedule_script(script)
                    loaded_count += 1
                    print(f"✓ 加载定时任务成功: {script.name} (ID: {script.id}, Cron: {script.cron_expression})")
                except Exception as e:
                    print(f"✗ 加载定时任务失败: {script.name} (ID: {script.id}), 错误: {str(e)}")
            
            print(f"定时任务加载完成: 成功加载 {loaded_count} 个任务")
        except Exception as e:
            print(f"加载定时任务时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _validate_cron_expression(self, cron_expr):
        """验证Cron表达式格式（简单验证）"""
        if not cron_expr:
            return False
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            return False
        # 简单格式检查：分钟 小时 日 月 星期
        for part in parts:
            if not (part.isdigit() or part == '*' or '/' in part or '-' in part or ',' in part):
                return False
        return True
    
    def get_all_scripts(self, page=1, per_page=20, name=None, script_type=None):
        """获取所有脚本（分页）"""
        query = ScriptManagement.query.filter_by(is_active=True)
        
        if name:
            query = query.filter(ScriptManagement.name.like(f'%{name}%'))
        if script_type:
            query = query.filter_by(script_type=script_type)
        
        query = query.order_by(ScriptManagement.id.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'data': [s.to_dict() for s in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    
    def get_script_by_id(self, script_id):
        """根据ID获取脚本"""
        script = ScriptManagement.query.filter_by(id=script_id, is_active=True).first()
        if not script:
            raise APIException('脚本不存在', 404)
        return script.to_dict()
    
    def create_script(self, data, current_user=None):
        """创建脚本"""
        # 检查名称是否重复
        if ScriptManagement.query.filter_by(name=data['name'], is_active=True).first():
            raise APIException('脚本名称已存在', 409)
        
        # 如果设置了定时任务，验证cron表达式
        if data.get('is_scheduled') and data.get('cron_expression'):
            if not self._validate_cron_expression(data['cron_expression']):
                raise APIException('Cron表达式格式错误', 400)
        
        script = ScriptManagement(
            name=data['name'],
            description=data.get('description', ''),
            script_type=data.get('script_type', 'python'),
            script_content=data['script_content'],
            file_path=data.get('file_path'),
            is_enabled=data.get('is_enabled', True),
            is_scheduled=data.get('is_scheduled', False),
            cron_expression=data.get('cron_expression'),
            timeout_seconds=data.get('timeout_seconds', 300),
            environment_vars=json.dumps(data.get('environment_vars', {})) if data.get('environment_vars') else None
        )
        if current_user:
            script.created_by = current_user.id
            script.updated_by = current_user.id
        
        db.session.add(script)
        db.session.commit()
        
        # 如果启用了定时任务，创建调度任务
        if script.is_scheduled and script.is_enabled and script.cron_expression:
            self._schedule_script(script)
        
        return script.to_dict()
    
    def update_script(self, script_id, data, current_user=None):
        """更新脚本"""
        script = ScriptManagement.query.filter_by(id=script_id, is_active=True).first()
        if not script:
            raise APIException('脚本不存在', 404)
        
        # 检查名称重复
        if 'name' in data and data['name'] != script.name:
            if ScriptManagement.query.filter_by(name=data['name'], is_active=True).first():
                raise APIException('脚本名称已存在', 409)
        
        # 验证cron表达式
        if data.get('is_scheduled') and data.get('cron_expression'):
            if not self._validate_cron_expression(data['cron_expression']):
                raise APIException('Cron表达式格式错误', 400)
        
        # 更新字段
        if 'name' in data:
            script.name = data['name']
        if 'description' in data:
            script.description = data.get('description')
        if 'script_type' in data:
            script.script_type = data['script_type']
        if 'script_content' in data:
            script.script_content = data['script_content']
        if 'file_path' in data:
            script.file_path = data.get('file_path')
        
        if current_user:
            script.updated_by = current_user.id
        if 'is_enabled' in data:
            script.is_enabled = data['is_enabled']
        if 'is_scheduled' in data:
            script.is_scheduled = data['is_scheduled']
        if 'cron_expression' in data:
            script.cron_expression = data.get('cron_expression')
        if 'timeout_seconds' in data:
            script.timeout_seconds = data.get('timeout_seconds', 300)
        if 'environment_vars' in data:
            script.environment_vars = json.dumps(data['environment_vars']) if data['environment_vars'] else None
        
        script.updated_at = datetime.now(tz_beijing)
        db.session.commit()
        
        # 更新定时任务
        if script.schedule_job_id and self.scheduler:
            try:
                self.scheduler.remove_job(script.schedule_job_id)
            except:
                pass
            script.schedule_job_id = None
        
        if script.is_scheduled and script.is_enabled and script.cron_expression:
            self._schedule_script(script)
        elif script.schedule_job_id:
            script.schedule_job_id = None
        
        db.session.commit()
        return script.to_dict()
    
    def delete_script(self, script_id):
        """删除脚本（软删除）"""
        script = ScriptManagement.query.filter_by(id=script_id, is_active=True).first()
        if not script:
            raise APIException('脚本不存在', 404)
        
        # 移除定时任务
        if script.schedule_job_id and self.scheduler:
            try:
                self.scheduler.remove_job(script.schedule_job_id)
            except:
                pass
        
        script.is_active = False
        script.is_enabled = False
        script.is_scheduled = False
        db.session.commit()
        
        return {'message': '脚本已删除'}
    
    def _schedule_script(self, script):
        """创建定时任务"""
        if not APSCHEDULER_AVAILABLE or not self.scheduler:
            raise APIException('定时任务功能不可用，请安装APScheduler', 500)
        
        try:
            # 解析cron表达式
            parts = script.cron_expression.strip().split()
            if len(parts) != 5:
                raise ValueError("Cron表达式格式错误")
            
            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4]
            )
            
            job_id = f"script_{script.id}"
            # 使用带应用上下文的包装函数，确保定时任务能访问数据库
            self.scheduler.add_job(
                func=self._execute_script_with_context,
                trigger=trigger,
                args=[script.id, 'scheduled', 'system'],
                id=job_id,
                replace_existing=True
            )
            
            script.schedule_job_id = job_id
            db.session.commit()
        except Exception as e:
            raise APIException(f'创建定时任务失败: {str(e)}', 500)
    
    def execute_script(self, script_id, execution_type='manual', triggered_by='system'):
        """执行脚本（手动或定时）
        注意：如果是定时任务调用，应该在应用上下文中调用此方法
        """
        try:
            script = ScriptManagement.query.filter_by(id=script_id, is_active=True).first()
        except RuntimeError as e:
            if "application context" in str(e).lower():
                raise RuntimeError(f"执行脚本时需要应用上下文。请使用 _execute_script_with_context 方法执行定时任务。错误: {str(e)}")
            raise
        
        if not script:
            raise APIException('脚本不存在', 404)
        
        if not script.is_enabled:
            raise APIException('脚本已禁用', 400)
        
        # 创建执行记录
        execution = ScriptExecutionHistory(
            script_id=script_id,
            execution_type=execution_type,
            status='running',
            triggered_by=triggered_by
        )
        db.session.add(execution)
        db.session.commit()
        execution_id = execution.id
        
        # 获取当前应用实例（用于在后台线程中创建应用上下文）
        try:
            app = current_app._get_current_object()
        except RuntimeError:
            # 如果没有current_app，使用self.app
            if self.app:
                app = self.app
            else:
                raise RuntimeError("无法获取Flask应用实例，无法在后台线程中执行脚本")
        
        # 在后台线程中执行脚本（传递script_id而不是script对象，避免DetachedInstanceError）
        thread = threading.Thread(
            target=self._run_script_background,
            args=(app, script_id, execution_id),
            daemon=True
        )
        thread.start()
        
        return execution_id
    
    def _run_script_background(self, app, script_id, execution_id):
        """在后台执行脚本"""
        # 在后台线程中创建应用上下文
        with app.app_context():
            execution = ScriptExecutionHistory.query.get(execution_id)
            if not execution:
                return
            
            # 在应用上下文中重新查询脚本对象
            script = ScriptManagement.query.get(script_id)
            if not script:
                execution.status = 'failed'
                execution.end_time = datetime.now(tz_beijing)
                execution.error_output = "脚本不存在"
                execution.exit_code = -1
                db.session.commit()
                return
            
            start_time = time.time()
            output = ""
            error_output = ""
            exit_code = None
            process = None
            
            try:
                # 解析环境变量
                env = os.environ.copy()
                if script.environment_vars:
                    try:
                        custom_env = json.loads(script.environment_vars)
                        env.update(custom_env)
                    except:
                        pass
                
                # 创建临时文件
                suffix_map = {
                    'python': '.py',
                    'shell': '.sh',
                    'bash': '.sh',
                    'sh': '.sh'
                }
                suffix = suffix_map.get(script.script_type.lower(), '.txt')
                
                with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
                    f.write(script.script_content)
                    temp_file = f.name
                
                try:
                    # 根据脚本类型执行
                    if script.script_type.lower() in ['python', 'py']:
                        cmd = ['python3', temp_file]
                    elif script.script_type.lower() in ['shell', 'bash', 'sh']:
                        os.chmod(temp_file, 0o755)
                        cmd = ['bash', temp_file]
                    else:
                        raise ValueError(f"不支持的脚本类型: {script.script_type}")
                    
                    # 执行脚本
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        env=env,
                        cwd=os.path.dirname(temp_file)
                    )
                    
                    self.running_tasks[execution_id] = process
                    
                    # 等待执行完成（带超时）
                    try:
                        stdout, stderr = process.communicate(timeout=script.timeout_seconds)
                        output = stdout or ""
                        error_output = stderr or ""
                        exit_code = process.returncode
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                        exit_code = -1
                        error_output = f"脚本执行超时（{script.timeout_seconds}秒）"
                    
                finally:
                    # 删除临时文件
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
                
                # 更新执行记录
                duration = time.time() - start_time
                execution.status = 'success' if exit_code == 0 else 'failed'
                execution.end_time = datetime.now(tz_beijing)
                execution.duration_seconds = round(duration, 2)
                execution.output = output[:50000]  # 限制输出长度
                execution.error_output = error_output[:50000]
                execution.exit_code = exit_code
                
                # 更新脚本统计
                script.total_executions += 1
                if exit_code == 0:
                    script.success_count += 1
                else:
                    script.failure_count += 1
                
                db.session.commit()
                
            except Exception as e:
                duration = time.time() - start_time
                execution.status = 'failed'
                execution.end_time = datetime.now(tz_beijing)
                execution.duration_seconds = round(duration, 2)
                execution.error_output = str(e)[:50000]
                execution.exit_code = -1
                
                script.total_executions += 1
                script.failure_count += 1
                db.session.commit()
            finally:
                if execution_id in self.running_tasks:
                    del self.running_tasks[execution_id]
    
    def get_execution_history(self, script_id=None, page=1, per_page=1, status=None):
        """获取执行记录（仅用于获取最新执行记录，用于查看功能）"""
        query = ScriptExecutionHistory.query.order_by(ScriptExecutionHistory.id.desc())
        
        if script_id:
            query = query.filter_by(script_id=script_id)
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'data': [e.to_dict() for e in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    
    def get_execution_by_id(self, execution_id):
        """获取执行记录详情"""
        execution = ScriptExecutionHistory.query.get(execution_id)
        if not execution:
            raise APIException('执行记录不存在', 404)
        return execution.to_dict()
    
    def cancel_execution(self, execution_id):
        """取消正在执行的脚本"""
        if execution_id not in self.running_tasks:
            raise APIException('执行任务不存在或已结束', 404)
        
        process = self.running_tasks[execution_id]
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
        
        execution = ScriptExecutionHistory.query.get(execution_id)
        if execution:
            execution.status = 'cancelled'
            execution.end_time = datetime.now(tz_beijing)
            db.session.commit()
        
        del self.running_tasks[execution_id]
        return {'message': '任务已取消'}


# 全局服务实例
script_management_service = ScriptManagementService()
