#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  MCP (Model Context Protocol) 服务
"""

import json
from typing import Dict, List, Any, Optional


class McpService:
    """MCP 服务类，提供 MCP 协议的基本功能示例"""
    
    @staticmethod
    def list_resources() -> Dict[str, Any]:
        """
        列出可用的 MCP 资源
        
        Returns:
            Dict: 包含资源列表的响应
        """
        try:
            # 示例资源列表
            resources = [
                {
                    "uri": "file:///example/config.json",
                    "name": "配置文件",
                    "description": "示例配置文件资源",
                    "mimeType": "application/json"
                },
                {
                    "uri": "file:///example/api-docs.json",
                    "name": "API 文档",
                    "description": "API 文档资源",
                    "mimeType": "application/json"
                },
                {
                    "uri": "file:///example/test-data.csv",
                    "name": "测试数据",
                    "description": "CSV 格式的测试数据",
                    "mimeType": "text/csv"
                }
            ]
            
            return {
                'success': True,
                'resources': resources,
                'count': len(resources)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'resources': []
            }
    
    @staticmethod
    def read_resource(uri: str) -> Dict[str, Any]:
        """
        读取指定的 MCP 资源
        
        Args:
            uri: 资源 URI
            
        Returns:
            Dict: 包含资源内容的响应
        """
        try:
            # 示例：根据 URI 返回不同的模拟数据
            if 'config.json' in uri:
                content = {
                    "app_name": "测试平台",
                    "version": "1.0.0",
                    "environment": "development",
                    "database": {
                        "host": "localhost",
                        "port": 3306,
                        "name": "test_db"
                    }
                }
                return {
                    'success': True,
                    'uri': uri,
                    'contents': [
                        {
                            'uri': uri,
                            'mimeType': 'application/json',
                            'text': json.dumps(content, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            elif 'api-docs.json' in uri:
                content = {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "测试平台 API",
                        "version": "1.0.0"
                    },
                    "paths": {
                        "/api/users": {
                            "get": {
                                "summary": "获取用户列表",
                                "responses": {
                                    "200": {
                                        "description": "成功"
                                    }
                                }
                            }
                        }
                    }
                }
                return {
                    'success': True,
                    'uri': uri,
                    'contents': [
                        {
                            'uri': uri,
                            'mimeType': 'application/json',
                            'text': json.dumps(content, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            elif 'test-data.csv' in uri:
                content = "id,name,age\n1,张三,25\n2,李四,30\n3,王五,28"
                return {
                    'success': True,
                    'uri': uri,
                    'contents': [
                        {
                            'uri': uri,
                            'mimeType': 'text/csv',
                            'text': content
                        }
                    ]
                }
            else:
                return {
                    'success': False,
                    'error': f'资源不存在: {uri}',
                    'uri': uri
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'uri': uri
            }
    
    @staticmethod
    def list_tools() -> Dict[str, Any]:
        """
        列出可用的 MCP 工具
        
        Returns:
            Dict: 包含工具列表的响应
        """
        try:
            tools = [
                {
                    "name": "get_weather",
                    "description": "获取指定城市的天气信息",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名称"
                            }
                        },
                        "required": ["city"]
                    }
                },
                {
                    "name": "calculate",
                    "description": "执行数学计算",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "数学表达式，例如: 2+2, 10*5"
                            }
                        },
                        "required": ["expression"]
                    }
                },
                {
                    "name": "format_json",
                    "description": "格式化 JSON 字符串",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "json_string": {
                                "type": "string",
                                "description": "要格式化的 JSON 字符串"
                            },
                            "indent": {
                                "type": "integer",
                                "description": "缩进空格数",
                                "default": 2
                            }
                        },
                        "required": ["json_string"]
                    }
                }
            ]
            
            return {
                'success': True,
                'tools': tools,
                'count': len(tools)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tools': []
            }
    
    @staticmethod
    def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用指定的 MCP 工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            Dict: 工具执行结果
        """
        try:
            if name == "get_weather":
                city = arguments.get('city', '')
                if not city:
                    return {
                        'success': False,
                        'error': '缺少必需参数: city'
                    }
                # 模拟天气数据
                weather_data = {
                    "city": city,
                    "temperature": "22°C",
                    "condition": "晴天",
                    "humidity": "60%",
                    "wind": "10 km/h"
                }
                return {
                    'success': True,
                    'content': [
                        {
                            'type': 'text',
                            'text': json.dumps(weather_data, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            
            elif name == "calculate":
                expression = arguments.get('expression', '')
                if not expression:
                    return {
                        'success': False,
                        'error': '缺少必需参数: expression'
                    }
                try:
                    # 安全的数学计算（仅支持基本运算）
                    result = eval(expression.replace(' ', ''))
                    return {
                        'success': True,
                        'content': [
                            {
                                'type': 'text',
                                'text': f"计算结果: {expression} = {result}"
                            }
                        ]
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'计算错误: {str(e)}'
                    }
            
            elif name == "format_json":
                json_string = arguments.get('json_string', '')
                indent = arguments.get('indent', 2)
                if not json_string:
                    return {
                        'success': False,
                        'error': '缺少必需参数: json_string'
                    }
                try:
                    parsed = json.loads(json_string)
                    formatted = json.dumps(parsed, ensure_ascii=False, indent=indent)
                    return {
                        'success': True,
                        'content': [
                            {
                                'type': 'text',
                                'text': formatted
                            }
                        ]
                    }
                except json.JSONDecodeError as e:
                    return {
                        'success': False,
                        'error': f'JSON 解析错误: {str(e)}'
                    }
            
            else:
                return {
                    'success': False,
                    'error': f'未知工具: {name}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def list_prompts() -> Dict[str, Any]:
        """
        列出可用的 MCP 提示模板
        
        Returns:
            Dict: 包含提示列表的响应
        """
        try:
            prompts = [
                {
                    "name": "code_review",
                    "description": "代码审查提示模板",
                    "arguments": [
                        {
                            "name": "code",
                            "description": "要审查的代码",
                            "required": True
                        },
                        {
                            "name": "language",
                            "description": "编程语言",
                            "required": False
                        }
                    ]
                },
                {
                    "name": "api_test_generator",
                    "description": "API 测试用例生成提示模板",
                    "arguments": [
                        {
                            "name": "api_endpoint",
                            "description": "API 端点",
                            "required": True
                        },
                        {
                            "name": "method",
                            "description": "HTTP 方法",
                            "required": False
                        }
                    ]
                }
            ]
            
            return {
                'success': True,
                'prompts': prompts,
                'count': len(prompts)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'prompts': []
            }
    
    @staticmethod
    def get_prompt(name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取指定的 MCP 提示模板
        
        Args:
            name: 提示名称
            arguments: 提示参数
            
        Returns:
            Dict: 提示内容
        """
        try:
            arguments = arguments or {}
            
            if name == "code_review":
                code = arguments.get('code', '')
                language = arguments.get('language', 'python')
                if not code:
                    return {
                        'success': False,
                        'error': '缺少必需参数: code'
                    }
                prompt_text = f"""请对以下 {language} 代码进行审查：

```{language}
{code}
```

请从以下方面进行审查：
1. 代码风格和规范
2. 潜在的错误和 bug
3. 性能优化建议
4. 安全性问题
5. 可维护性建议"""
                
                return {
                    'success': True,
                    'messages': [
                        {
                            'role': 'user',
                            'content': {
                                'type': 'text',
                                'text': prompt_text
                            }
                        }
                    ]
                }
            
            elif name == "api_test_generator":
                api_endpoint = arguments.get('api_endpoint', '')
                method = arguments.get('method', 'GET')
                if not api_endpoint:
                    return {
                        'success': False,
                        'error': '缺少必需参数: api_endpoint'
                    }
                prompt_text = f"""请为以下 API 生成测试用例：

API 端点: {api_endpoint}
HTTP 方法: {method}

请生成包含以下内容的测试用例：
1. 正常场景测试
2. 边界值测试
3. 异常场景测试
4. 性能测试建议"""
                
                return {
                    'success': True,
                    'messages': [
                        {
                            'role': 'user',
                            'content': {
                                'type': 'text',
                                'text': prompt_text
                            }
                        }
                    ]
                }
            
            else:
                return {
                    'success': False,
                    'error': f'未知提示: {name}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

