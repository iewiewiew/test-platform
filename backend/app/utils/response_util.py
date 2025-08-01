#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author       weimenghua
@time         2025/05/13 11:31
@description  API 响应封装类
"""

import json
from typing import Any, Dict, List, Optional, Tuple, Union

from .log_util import Logger

logger = Logger()


class APIResponse:
    """封装API响应处理"""

    def __init__(self, response: Dict[str, Any]):
        """
        初始化API响应

        :param response: 原始响应字典，包含status、data、headers等字段
        """
        self.raw_response = response
        self.status_code = response.get('status')
        self.data = self._parse_data(response.get('data', ''))
        self.headers = response.get('headers', {})

    def _parse_data(self, data: str) -> Optional[Dict[str, Any]]:
        """
        解析响应数据

        :param data: 原始响应数据字符串
        :return: 解析后的字典或None
        """
        if not data or not data.strip():
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse response data: {data}")
            return None

    @property
    def is_not_found(self) -> bool:
        """
        判断资源是否存在

        :return: 状态码为404返回True，否则返回False
        """
        return self.status_code == 404

    # @todo 断言响应状态码不生效
    # def assert_status(self, status: Union[int, Tuple[int, ...]] = (200, 201, 204),
    def assert_status(self, status: Union[int, Tuple[int, ...]], message: str = None) -> 'APIResponse':
        """
        断言响应状态码

        :param status: 期望的状态码或状态码元组，默认为成功状态码(200, 201, 204)
        :param message: 自定义错误消息
        :return: 返回self以支持链式调用
        :raises AssertionError: 当状态码不匹配时抛出
        """
        if isinstance(status, int):
            status = (status,)

        if message is None:
            if status == (200, 201, 204):
                message = f"API请求失败，期望成功状态码(200,201,204)，实际状态码: {self.status_code}"
            else:
                message = f"状态码断言失败，期望: {status}，实际: {self.status_code}"

        assert self.status_code in status, message
        return self

    def assert_not_found(self, message: str = "资源未找到"):
        """
        断言资源不存在

        :param message: 自定义错误消息
        :raises AssertionError: 当状态码不是404时抛出
        """
        assert self.is_not_found, f"{message}, 状态码: {self.status_code}"

    def assert_value(self, condition: bool, message: str = "断言失败"):
        """
        通用断言方法，验证任意条件

        :param condition: 要验证的条件表达式
        :param message: 自定义错误消息
        :raises AssertionError: 当条件为False时抛出
        """
        logger.info(f"判断条件 {condition}")
        assert condition, message
        return self  # 支持链式调用

    def assert_data_field(self, field_path: str, expected_value: Any = None,
                          message: str = None, comparison: str = "=="):
        """
        断言响应数据中的字段值

        :param field_path: 字段路径，如 'data.id' 或 'items[0].name'
        :param expected_value: 期望值
        :param message: 自定义错误消息
        :param comparison: 比较运算符 (==, !=, >, <, >=, <=)
        :raises AssertionError: 当断言失败时抛出
        """
        if self.data is None:
            raise AssertionError("响应数据为空，无法断言字段值")

        # 获取字段值
        try:
            actual_value = self._get_nested_value(self.data, field_path)
        except (KeyError, IndexError, TypeError) as e:
            raise AssertionError(f"无法获取字段 '{field_path}': {str(e)}")

        # 默认错误消息
        if message is None:
            message = f"字段 '{field_path}' 断言失败: {actual_value} {comparison} {expected_value}"

        # 执行比较
        if comparison == "==":
            assert actual_value == expected_value, message
        elif comparison == "!=":
            assert actual_value != expected_value, message
        elif comparison == ">":
            assert actual_value > expected_value, message
        elif comparison == "<":
            assert actual_value < expected_value, message
        elif comparison == ">=":
            assert actual_value >= expected_value, message
        elif comparison == "<=":
            assert actual_value <= expected_value, message
        else:
            raise ValueError(f"不支持的比较运算符: {comparison}")

        return self  # 支持链式调用

    def _get_nested_value(self, data: Union[Dict, List], path: str) -> Any:
        """
        获取嵌套数据结构中的值

        :param data: 字典或列表
        :param path: 字段路径，如 'data.id' 或 'items[0].name'
        :return: 获取到的值
        """
        parts = path.split('.')
        current = data

        for part in parts:
            if '[' in part and ']' in part:
                # 处理数组索引，如 items[0]
                key = part.split('[')[0]
                index = int(part.split('[')[1].split(']')[0])
                current = current[key][index]
            else:
                current = current[part]

        return current