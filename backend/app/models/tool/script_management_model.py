#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/26
@description  自动化脚本管理实体类
"""

from ...core.database import db, datetime, tz_beijing
from ...models.base.base_model import BaseModel


class ScriptManagement(BaseModel):
    """自动化脚本管理模型"""
    __tablename__ = 'scripts'

    # 基础信息
    name = db.Column(db.String(100), nullable=False, comment='脚本名称')
    description = db.Column(db.Text, comment='脚本描述')
    script_type = db.Column(db.String(20), nullable=False, default='python', comment='脚本类型：python/shell/bash等')
    script_content = db.Column(db.Text, nullable=False, comment='脚本内容')
    file_path = db.Column(db.String(255), comment='上传文件路径（如果有）')
    
    # 执行配置
    is_enabled = db.Column(db.Boolean, default=True, nullable=False, comment='是否启用')
    timeout_seconds = db.Column(db.Integer, default=300, comment='超时时间（秒）')
    environment_vars = db.Column(db.Text, comment='环境变量（JSON格式）')
    
    # 定时任务配置
    is_scheduled = db.Column(db.Boolean, default=False, nullable=False, comment='是否定时执行')
    cron_expression = db.Column(db.String(100), comment='Cron表达式，如：0 0 * * *（每天凌晨）')
    schedule_job_id = db.Column(db.String(100), comment='定时任务ID（APScheduler）')
    
    # 统计信息
    total_executions = db.Column(db.Integer, default=0, comment='总执行次数')
    success_count = db.Column(db.Integer, default=0, comment='成功次数')
    failure_count = db.Column(db.Integer, default=0, comment='失败次数')

    def to_dict(self):
        """
        将脚本管理对象转换为字典

        Returns:
            dict: 脚本管理数据的字典表示
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'script_type': self.script_type,
            'script_content': self.script_content,
            'file_path': self.file_path,
            'is_enabled': self.is_enabled,
            'is_scheduled': self.is_scheduled,
            'cron_expression': self.cron_expression,
            'timeout_seconds': self.timeout_seconds,
            'environment_vars': self.environment_vars,
            'total_executions': self.total_executions,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'creator_name': self.creator.username if self.creator else None,
            'updater_name': self.updater.username if self.updater else None
        }

    def __repr__(self):
        return f'<ScriptManagement {self.name}>'


class ScriptExecutionHistory(BaseModel):
    """脚本执行历史记录模型"""
    __tablename__ = 'script_execution_histories'

    script_id = db.Column(db.Integer, db.ForeignKey('scripts.id'), nullable=False, comment='脚本ID')
    execution_type = db.Column(db.String(20), default='manual', comment='执行类型：manual/scheduled')
    status = db.Column(db.String(20), default='running', comment='执行状态：running/success/failed/cancelled')
    start_time = db.Column(db.DateTime, default=lambda: datetime.now(tz_beijing), nullable=False, comment='开始时间')
    end_time = db.Column(db.DateTime, comment='结束时间')
    duration_seconds = db.Column(db.Float, comment='执行时长（秒）')
    output = db.Column(db.Text, comment='输出内容（stdout）')
    error_output = db.Column(db.Text, comment='错误输出（stderr）')
    exit_code = db.Column(db.Integer, comment='退出码')
    triggered_by = db.Column(db.String(50), comment='触发者（用户ID或系统）')
    
    # 关联关系
    script = db.relationship('ScriptManagement', backref='executions', lazy=True)

    def to_dict(self):
        """
        将脚本执行历史对象转换为字典

        Returns:
            dict: 脚本执行历史数据的字典表示
        """
        return {
            'id': self.id,
            'script_id': self.script_id,
            'script_name': self.script.name if self.script else None,
            'execution_type': self.execution_type,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'output': self.output,
            'error_output': self.error_output,
            'exit_code': self.exit_code,
            'triggered_by': self.triggered_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'creator_name': self.creator.username if self.creator else None,
            'updater_name': self.updater.username if self.updater else None
        }

    def __repr__(self):
        return f'<ScriptExecutionHistory {self.id}>'
