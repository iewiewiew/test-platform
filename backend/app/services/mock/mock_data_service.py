#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/2 15:49
@description  模拟数据生成服务 - 使用Faker库优化版本
"""

import random
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union

from faker import Faker


class MockDataService:
    """模拟数据生成服务"""

    # 初始化Faker实例
    _fake = Faker('zh_CN')  # 指定中文环境

    # 支持的字段类型
    FIELD_TYPES = {'name': '姓名', 'id_card': '身份证号', 'phone': '手机号', 'email': '邮箱', 'address': '地址',
        'date': '日期', 'datetime': '日期时间', 'text': '文本', 'number': '数字', 'boolean': '布尔值',
        'company': '公司名称', 'bank_card': '银行卡号', 'age': '年龄', 'province': '省份', 'city': '城市',
        'postcode': '邮编', 'job': '职业', 'ssn': '社保号', 'license_plate': '车牌号'}

    @classmethod
    def set_locale(cls, locale: str = 'zh_CN'):
        """设置Faker语言环境"""
        cls._fake = Faker(locale)

    @staticmethod
    def get_supported_field_types() -> Dict[str, str]:
        """获取支持的字段类型"""
        return MockDataService.FIELD_TYPES

    @classmethod
    def generate_mock_data(cls, fields: List[Dict[str, Any]], count: int = 1) -> List[Dict[str, Any]]:
        """
        生成模拟数据

        Args:
            fields: 字段配置列表，每个字段包含name、type和options
            count: 生成数据条数

        Returns:
            生成的模拟数据列表
        """
        result = []

        for _ in range(count):
            item = {}
            for field_config in fields:
                field_name = field_config.get('name')
                field_type = field_config.get('type')
                options = field_config.get('options', {})

                if field_name and field_type:
                    value = cls._generate_field_value(field_type, options)
                    item[field_name] = value

            result.append(item)

        return result

    @classmethod
    def _generate_field_value(cls, field_type: str, options: Dict[str, Any] = None) -> Any:
        """根据字段类型生成对应的值"""
        options = options or {}

        # 使用字典映射替代if-else链，提高可读性和可维护性
        field_generators = {'name': lambda: cls._fake.name(), 'id_card': lambda: cls._fake.ssn(),  # Faker中的ssn方法生成身份证号
            'phone': lambda: cls._fake.phone_number(), 'email': lambda: cls._fake.email(),
            'address': lambda: cls._fake.address(), 'date': lambda: cls._generate_date(options),
            'datetime': lambda: cls._generate_datetime(options), 'text': lambda: cls._generate_text(options),
            'number': lambda: cls._generate_number(options), 'boolean': lambda: cls._fake.boolean(),
            'company': lambda: cls._fake.company(), 'bank_card': lambda: cls._fake.credit_card_number(),
            'age': lambda: cls._generate_age(options), 'province': lambda: cls._fake.province(),
            'city': lambda: cls._fake.city(), 'postcode': lambda: cls._fake.postcode(), 'job': lambda: cls._fake.job(),
            'ssn': lambda: cls._fake.ssn(), 'license_plate': lambda: cls._fake.license_plate()}

        generator = field_generators.get(field_type)
        if generator:
            return generator()
        else:
            return f"未知类型: {field_type}"

    @staticmethod
    def _generate_date(options: Dict[str, Any]) -> str:
        """生成日期"""
        start_date = options.get('start_date', '2000-01-01')
        end_date = options.get('end_date', '2023-12-31')

        try:
            # 使用Faker的date_between方法
            fake_instance = MockDataService._fake
            return fake_instance.date_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d')
        except Exception:
            # 备用方案
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            random_date = start + timedelta(days=random.randint(0, (end - start).days))
            return random_date.strftime('%Y-%m-%d')

    @staticmethod
    def _generate_datetime(options: Dict[str, Any]) -> str:
        """生成日期时间"""
        start_date = options.get('start_date', '2000-01-01')
        end_date = options.get('end_date', '2023-12-31')

        try:
            # 使用Faker的date_time_between方法
            fake_instance = MockDataService._fake
            return fake_instance.date_time_between(start_date=start_date, end_date=end_date).strftime(
                '%Y-%m-%d %H:%M:%S')
        except Exception:
            # 备用方案
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            random_datetime = start + timedelta(days=random.randint(0, (end - start).days), hours=random.randint(0, 23),
                minutes=random.randint(0, 59), seconds=random.randint(0, 59))
            return random_datetime.strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def _generate_text(cls, options: Dict[str, Any]) -> str:
        """生成文本"""
        min_length = options.get('min_length', 10)
        max_length = options.get('max_length', 50)

        # 使用Faker的text方法生成更真实的文本
        text = cls._fake.text(max_nb_chars=max_length)
        if len(text) < min_length:
            # 如果生成的文本太短，使用多个句子组合
            sentences = []
            while len(''.join(sentences)) < min_length:
                sentences.append(cls._fake.sentence())
            text = ' '.join(sentences)

        return text[:max_length]

    @classmethod
    def _generate_number(cls, options: Dict[str, Any]) -> Union[int, float]:
        """生成数字"""
        min_value = options.get('min_value', 0)
        max_value = options.get('max_value', 100)
        decimals = options.get('decimals', 0)

        if decimals == 0:
            # 整数
            return cls._fake.random_int(min=min_value, max=max_value)
        else:
            # 浮点数
            number = cls._fake.pyfloat(left_digits=len(str(max_value)) - decimals, right_digits=decimals, positive=True,
                min_value=min_value, max_value=max_value)
            return round(number, decimals)

    @staticmethod
    def _generate_age(options: Dict[str, Any]) -> int:
        """生成年龄"""
        min_age = options.get('min_age', 18)
        max_age = options.get('max_age', 60)
        fake_instance = MockDataService._fake
        return fake_instance.random_int(min=min_age, max=max_age)

    @classmethod
    def generate_bulk_data(cls, field_types: List[str], count: int = 10) -> List[Dict[str, Any]]:
        """
        批量生成数据（简化版）

        Args:
            field_types: 字段类型列表
            count: 数据条数

        Returns:
            生成的模拟数据列表
        """
        fields = [{'name': f'field_{i}', 'type': field_type} for i, field_type in enumerate(field_types)]
        return cls.generate_mock_data(fields, count)

    @staticmethod
    def validate_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证生成的数据格式

        Args:
            data: 待验证的数据

        Returns:
            验证结果
        """
        validation_result = {'is_valid': True, 'errors': []}

        # 邮箱验证
        if 'email' in data:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                validation_result['is_valid'] = False
                validation_result['errors'].append('邮箱格式无效')

        # 手机号验证（简单验证）
        if 'phone' in data:
            phone_pattern = r'^1[3-9]\d{9}$'
            if not re.match(phone_pattern, data['phone']):
                validation_result['is_valid'] = False
                validation_result['errors'].append('手机号格式无效')

        return validation_result


# 使用示例
if __name__ == "__main__":
    # 示例字段配置
    sample_fields = [{'name': '姓名', 'type': 'name'},
        {'name': '年龄', 'type': 'age', 'options': {'min_age': 20, 'max_age': 50}}, {'name': '邮箱', 'type': 'email'},
        {'name': '手机号', 'type': 'phone'}, {'name': '地址', 'type': 'address'}, {'name': '公司', 'type': 'company'},
        {'name': '出生日期', 'type': 'date', 'options': {'start_date': '1980-01-01', 'end_date': '2000-12-31'}}]

    # 生成测试数据
    test_data = MockDataService.generate_mock_data(sample_fields, 3)

    print("生成的测试数据:")
    for i, data in enumerate(test_data, 1):
        print(f"\n第{i}条数据:")
        for key, value in data.items():
            print(f"  {key}: {value}")

        # 验证数据
        validation = MockDataService.validate_data(data)
        print(f"  数据验证: {'通过' if validation['is_valid'] else '失败'}")
        if validation['errors']:
            print(f"  错误信息: {', '.join(validation['errors'])}")

    # 显示支持的字段类型
    print(f"\n支持的字段类型: {list(MockDataService.get_supported_field_types().keys())}")

    # 测试批量生成
    print("\n批量生成测试:")
    bulk_data = MockDataService.generate_bulk_data(['name', 'email', 'phone'], 2)
    for i, data in enumerate(bulk_data, 1):
        print(f"批量数据{i}: {data}")
