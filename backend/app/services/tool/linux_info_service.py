# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/19 17:10
@description
"""

from io import StringIO

import paramiko
from sqlalchemy import or_

from ...core.database import db
from ...models.tool.linux_info_model import LinuxInfo


class LinuxInfoService:

    @staticmethod
    def get_all_servers(page=1, per_page=10, server_name=None, host=None):
        """获取所有服务器信息（支持分页和搜索）"""
        
        # 基础查询
        query = LinuxInfo.query
        
        # 添加搜索条件
        conditions = []
        if server_name:
            conditions.append(LinuxInfo.server_name.ilike(f'%{server_name}%'))
        if host:
            conditions.append(LinuxInfo.host.ilike(f'%{host}%'))
        
        # 如果存在搜索条件，应用过滤
        if conditions:
            query = query.filter(or_(*conditions))
        
        # 排序和分页
        pagination = query.order_by(LinuxInfo.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'data': [server.to_dict() for server in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }

    @staticmethod
    def get_server_by_id(server_id):
        return LinuxInfo.query.get(server_id)

    @staticmethod
    def create_server(data, current_user=None):
        if LinuxInfo.query.filter_by(host=data['host']).first():
            raise ValueError('Host already exists')

        server = LinuxInfo(server_name=data['server_name'], host=data['host'], port=data.get('port', 22),
            username=data['username'], password=data.get('password'), private_key=data.get('private_key'),
            description=data.get('description'))
        if current_user:
            server.created_by = current_user.id
            server.updated_by = current_user.id
        db.session.add(server)
        db.session.commit()
        return server

    @staticmethod
    def update_server(server_id, data, current_user=None):
        server = LinuxInfo.query.get(server_id)
        if not server:
            return None

        for key, value in data.items():
            if hasattr(server, key) and key not in ['created_by', 'updated_by']:  # 避免直接设置这些字段
                setattr(server, key, value)
        
        if current_user:
            server.updated_by = current_user.id

        db.session.commit()
        return server

    @staticmethod
    def delete_server(server_id):
        server = LinuxInfo.query.get(server_id)
        if server:
            db.session.delete(server)
            db.session.commit()
            return True
        return False

    @staticmethod
    def execute_command(server_id, command):
        server = LinuxInfo.query.get(server_id)
        if not server:
            return {'success': False, 'error': 'Server not found'}

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 连接参数
            connect_params = {'hostname': server.host, 'port': server.port, 'username': server.username, 'timeout': 30}

            if server.private_key:
                # 使用私钥认证
                private_key = paramiko.RSAKey.from_private_key(StringIO(server.private_key))
                connect_params['pkey'] = private_key
            else:
                # 使用密码认证
                connect_params['password'] = server.password

            ssh.connect(**connect_params)

            # 执行命令
            stdin, stdout, stderr = ssh.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            ssh.close()

            return {'success': True, 'output': output, 'error': error, 'exit_status': exit_status}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_server_info(server_id):
        """获取服务器基本信息"""
        commands = {'hostname': 'hostname', 'os_info': 'cat /etc/os-release', 'kernel': 'uname -r', 'uptime': 'uptime',
            'memory': 'free -h', 'disk': 'df -h', 'cpu_info': 'lscpu'}

        results = {}
        for key, command in commands.items():
            result = LinuxInfoService.execute_command(server_id, command)
            if result['success']:
                results[key] = result['output']
            else:
                results[key] = f"Error: {result['error']}"

        return results

    @staticmethod
    def get_server_metrics(server_id):
        """获取服务器资源使用指标（CPU/内存/磁盘/负载/运行时长）"""
        # 使用更稳定的命令以便解析
        commands = {
            'cpu': "top -bn1 | grep 'Cpu(s)' || mpstat 1 1 | tail -1",
            'memory': "free -m",
            'disk_total': "df -P -k --total | tail -1",
            'loadavg': "cat /proc/loadavg || uptime",
            'uptime': "uptime -p || uptime"
        }

        raw = {}
        for key, cmd in commands.items():
            res = LinuxInfoService.execute_command(server_id, cmd)
            raw[key] = res['output'] if res.get('success') else ''

        cpu_usage = None
        try:
            line = raw['cpu']
            # 兼容 top 输出: Cpu(s):  3.0%us,  1.0%sy,  0.0%ni, 95.5%id, ...
            import re
            m = re.search(r"(\d+\.?\d*)%id", line)
            if m:
                idle = float(m.group(1))
                cpu_usage = round(100 - idle, 2)
            else:
                # 兼容 mpstat: all  3.00 1.00 0.00 95.50 ...
                parts = [p for p in line.strip().split() if p]
                if len(parts) >= 12:
                    idle = float(parts[-1])
                    cpu_usage = round(100 - idle, 2)
        except Exception:
            cpu_usage = None

        memory_usage = None
        try:
            lines = raw['memory'].strip().split('\n')
            # free -m 第二行一般为 Mem:
            for l in lines:
                if l.lower().startswith('mem:') or l.startswith('Mem:'):
                    parts = [p for p in l.split() if p and p != 'Mem:']
                    if len(parts) >= 2:
                        total = float(parts[0])
                        used = float(parts[1])
                        if total > 0:
                            memory_usage = round((used / total) * 100, 2)
                    break
        except Exception:
            memory_usage = None

        disk_usage = None
        try:
            # df --total 最后一行: total <1K-blocks> <Used> <Available> <Use%> <Mounted on>
            parts = [p for p in raw['disk_total'].strip().split() if p]
            if len(parts) >= 5:
                use_pct = parts[4]
                if use_pct.endswith('%'):
                    disk_usage = float(use_pct[:-1])
        except Exception:
            disk_usage = None

        load_average = None
        try:
            la = raw['loadavg'].strip()
            # /proc/loadavg: "0.20 0.18 0.14 1/123 4567"
            tokens = la.split()
            if len(tokens) >= 3:
                load_average = {
                    '1min': float(tokens[0]),
                    '5min': float(tokens[1]),
                    '15min': float(tokens[2])
                }
        except Exception:
            load_average = None

        # 解析 uptime 为更易读的字符串
        uptime_text = None
        try:
            ut = raw['uptime'].strip()
            # 优先处理 `uptime -p` 格式: "up 5 days,  2 hours,  15 minutes"
            if 'up ' in ut and ('minute' in ut or 'hour' in ut or 'day' in ut):
                uptime_text = ut.replace('up ', '').strip()
            else:
                # 兜底解析 `uptime` 常规输出: "10:30:45 up 5 days,  2:15,  1 user,  load average: ..."
                # 提取 "up ... ," 之间的内容
                import re
                m = re.search(r"up\s+([^,]+)", ut)
                if m:
                    uptime_text = m.group(1).strip()
        except Exception:
            uptime_text = None

        # 计算整体状态，简单基于最高资源使用率
        def decide_status(cpu, mem, disk):
            values = [v for v in [cpu, mem, disk] if isinstance(v, (int, float))]
            if not values:
                return 'unknown'
            worst = max(values)
            if worst >= 80:
                return 'critical'
            if worst >= 60:
                return 'warning'
            return 'healthy'

        status = decide_status(cpu_usage, memory_usage, disk_usage)

        return {
            'server_id': server_id,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage,
            'load_average': load_average,
            'uptime': uptime_text,
            'status': status,
            'raw': raw
        }

    @staticmethod
    def get_all_server_metrics():
        """获取所有服务器的资源使用指标"""
        servers = LinuxInfo.query.all()
        results = []
        for s in servers:
            metrics = LinuxInfoService.get_server_metrics(s.id)
            metrics.update({'server_name': s.server_name, 'host': s.host})
            results.append(metrics)
        return results
