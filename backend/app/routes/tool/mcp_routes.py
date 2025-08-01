#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  MCP (Model Context Protocol) 路由
"""

from flask import Blueprint, request, jsonify

from ...services.tool.mcp_service import McpService

mcp_bp = Blueprint('mcp', __name__)


# ==================== MCP 资源管理 ====================

@mcp_bp.route('/mcp/resources', methods=['GET'])
def list_resources():
    """列出所有可用的 MCP 资源"""
    try:
        result = McpService.list_resources()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mcp_bp.route('/mcp/resources/read', methods=['POST'])
def read_resource():
    """读取指定的 MCP 资源"""
    try:
        data = request.get_json()
        uri = data.get('uri', '')
        
        if not uri:
            return jsonify({'success': False, 'error': 'URI 不能为空'}), 400
        
        result = McpService.read_resource(uri)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== MCP 工具管理 ====================

@mcp_bp.route('/mcp/tools', methods=['GET'])
def list_tools():
    """列出所有可用的 MCP 工具"""
    try:
        result = McpService.list_tools()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mcp_bp.route('/mcp/tools/call', methods=['POST'])
def call_tool():
    """调用指定的 MCP 工具"""
    try:
        data = request.get_json()
        name = data.get('name', '')
        arguments = data.get('arguments', {})
        
        if not name:
            return jsonify({'success': False, 'error': '工具名称不能为空'}), 400
        
        result = McpService.call_tool(name, arguments)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== MCP 提示管理 ====================

@mcp_bp.route('/mcp/prompts', methods=['GET'])
def list_prompts():
    """列出所有可用的 MCP 提示模板"""
    try:
        result = McpService.list_prompts()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mcp_bp.route('/mcp/prompts/get', methods=['POST'])
def get_prompt():
    """获取指定的 MCP 提示模板"""
    try:
        data = request.get_json()
        name = data.get('name', '')
        arguments = data.get('arguments', {})
        
        if not name:
            return jsonify({'success': False, 'error': '提示名称不能为空'}), 400
        
        result = McpService.get_prompt(name, arguments)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

