# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/8/4 14:27
@description  生成随机数
"""


class DynamicDataProcessor:
    @staticmethod
    def process_template(template, request_data):
        """更安全的模板处理方法"""
        if isinstance(template, dict):
            return {k: DynamicDataProcessor._process_value(v, request_data) for k, v in template.items()}
        elif isinstance(template, list):
            return [DynamicDataProcessor._process_value(item, request_data) for item in template]
        return template

    @staticmethod
    def _process_value(value, request_data):
        """处理单个值"""
        if isinstance(value, str):
            try:
                # 先处理动态标记
                value = DynamicDataProcessor._replace_dynamic_tags(value, request_data)
                # 再处理随机标记
                value = RandomDataGenerator._replace_random_tags(value)
            except Exception as e:
                return f"[PROCESSING_ERROR:{str(e)}]"
        elif isinstance(value, (dict, list)):
            value = DynamicDataProcessor.process_template(value, request_data)
        return value

    @staticmethod
    def _replace_dynamic_tags(template, request_data):
        """更安全的动态标记替换方法"""
        if not isinstance(template, str):
            return template

        # 使用更简单的正则表达式
        def replace_tag(match):
            try:
                full_tag = match.group(1)
                if not full_tag.startswith('request.'):
                    return match.group(0)

                parts = full_tag.split('.')
                if len(parts) != 3:
                    return match.group(0)

                source = parts[1]
                key = parts[2]

                if source in ['headers', 'args', 'json', 'form']:
                    return str(request_data.get(source, {}).get(key, ''))
                return match.group(0)
            except:
                return match.group(0)

        return re.sub(r'\{(.+?)\}', replace_tag, template)


import random
import string
from datetime import datetime, timedelta
import re
from faker import Faker  # 需要安装：pip install faker


class RandomDataGenerator:
    _fake = Faker('zh_CN')  # 中文数据生成器

    @staticmethod
    def phone():
        """随机手机号"""
        prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                    '150', '151', '152', '153', '155', '156', '157', '158', '159',
                    '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
        return random.choice(prefixes) + ''.join(random.choices('0123456789', k=8))

    @staticmethod
    def id_card():
        """生成18位身份证号"""
        # 1. 生成前6位地区码
        region_code = random.choice(['110', '120', '130', '140'])  # 简化地区码
        region_code += ''.join(random.choices('0123456789', k=3))  # 补齐6位

        # 2. 生成出生日期(8位)
        start_date = datetime(1950, 1, 1)
        end_date = datetime(2000, 12, 31)
        random_days = random.randint(0, (end_date - start_date).days)
        birth_date = (start_date + timedelta(days=random_days)).strftime('%Y%m%d')

        # 3. 生成顺序码(3位)
        seq_code = ''.join(random.choices('0123456789', k=3))

        # 前17位
        first_17 = region_code + birth_date + seq_code

        # 确保长度是17位
        if len(first_17) != 17:
            raise ValueError(f"Invalid first_17 length: {len(first_17)}")

        # 4. 计算校验码
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

        try:
            total = sum(int(first_17[i]) * weights[i] for i in range(17))
            check_code = check_codes[total % 11]
        except Exception as e:
            raise ValueError(f"Failed to calculate check code: {e}, first_17: {first_17}")

        return first_17 + check_code

    @staticmethod
    def email():
        """随机邮箱"""
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', '163.com', 'qq.com']
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))
        return f"{name}@{random.choice(domains)}"

    @staticmethod
    def name():
        """随机中文姓名"""
        return RandomDataGenerator._fake.name()

    @staticmethod
    def address():
        """随机地址"""
        return RandomDataGenerator._fake.address()

    @staticmethod
    def text(length=10):
        """随机文本"""
        return RandomDataGenerator._fake.text(max_nb_chars=length)

    @staticmethod
    def date(start_date="1990-01-01", end_date="today", fmt="%Y-%m-%d"):
        """随机日期"""
        try:
            if isinstance(start_date, str) and start_date != "today":
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str) and end_date != "today":
                end_date = datetime.strptime(end_date, "%Y-%m-%d")

            random_date = RandomDataGenerator._fake.date_between(
                start_date=start_date,
                end_date=end_date
            )
            return random_date.strftime(fmt)
        except Exception as e:
            print(f"Error generating random date: {e}")
            return datetime.now().strftime(fmt)
    @staticmethod
    def datetime(start_date="-30y", end_date="now", fmt="%Y-%m-%d %H:%M:%S"):
        """随机日期时间"""
        return RandomDataGenerator._fake.date_time_between(start_date=start_date, end_date=end_date).strftime(fmt)

    @staticmethod
    def now(fmt="%Y-%m-%d %H:%M:%S"):
        """获取当前时间"""
        return datetime.now().strftime(fmt)
    @staticmethod
    def ipv4():
        """随机IPv4地址"""
        return RandomDataGenerator._fake.ipv4()

    @staticmethod
    def company():
        """随机公司名"""
        return RandomDataGenerator._fake.company()

    @staticmethod
    def job():
        """随机职位"""
        return RandomDataGenerator._fake.job()

    @staticmethod
    def word():
        """随机单词"""
        return RandomDataGenerator._fake.word()

    @staticmethod
    def sentence(nb_words=6):
        """随机句子"""
        return RandomDataGenerator._fake.sentence(nb_words=nb_words)

    @staticmethod
    def float(min=0, max=10000, decimal=2):
        """随机浮点数"""
        return round(random.uniform(min, max), decimal)

    @staticmethod
    def int(min=0, max=10000):
        """随机整数"""
        return random.randint(min, max)

    @staticmethod
    def boolean():
        """随机布尔值"""
        return random.choice([True, False])

    @staticmethod
    def uuid():
        """随机UUID"""
        return str(RandomDataGenerator._fake.uuid4())

    @staticmethod
    def color():
        """随机颜色"""
        return RandomDataGenerator._fake.hex_color()

    @staticmethod
    def image_url(width=200, height=200):
        """随机图片URL"""
        return RandomDataGenerator._fake.image_url(width=width, height=height)

    @staticmethod
    def _replace_random_tags(template):
        """处理随机标记的模板"""
        if not isinstance(template, str):
            return template

        def replace_random(match):
            try:
                expr = match.group(1).strip()

                # 基本随机标记
                if expr == 'phone': return RandomDataGenerator.phone()
                if expr == 'id_card': return RandomDataGenerator.id_card()
                if expr == 'email': return RandomDataGenerator.email()
                if expr == 'name': return RandomDataGenerator.name()
                if expr == 'address': return RandomDataGenerator.address()
                if expr == 'text': return RandomDataGenerator.text()
                if expr == 'datetime': return RandomDataGenerator.datetime()
                if expr == 'now': return RandomDataGenerator.now()
                if expr == 'ipv4': return RandomDataGenerator.ipv4()
                if expr == 'company': return RandomDataGenerator.company()
                if expr == 'job': return RandomDataGenerator.job()
                if expr == 'word': return RandomDataGenerator.word()
                if expr == 'sentence': return RandomDataGenerator.sentence()
                if expr == 'float': return RandomDataGenerator.float()
                if expr == 'int': return RandomDataGenerator.int()
                if expr == 'boolean': return str(RandomDataGenerator.boolean())
                if expr == 'uuid': return RandomDataGenerator.uuid()
                if expr == 'color': return RandomDataGenerator.color()
                if expr == 'image_url': return RandomDataGenerator.image_url()
                if expr.startswith('date['):
                    # 处理 ${date[%Y-%m-%d,1990-01-01,2000-12-31]} 格式
                    try:
                        params = expr[5:-1].split(',')
                        fmt = params[0].strip().strip('"\'')
                        start = params[1].strip().strip('"\'') if len(params) > 1 else "1990-01-01"
                        end = params[2].strip().strip('"\'') if len(params) > 2 else "today"
                        return RandomDataGenerator.date(start, end, fmt)
                    except Exception as e:
                        print(f"Error processing date tag: {e}")
                        return datetime.now().strftime("%Y-%m-%d")

                # 带参数的随机标记
                if expr.startswith('int['):
                    params = expr[4:-1].split(',')
                    min_val = int(params[0].strip())
                    max_val = int(params[1].strip())
                    return str(RandomDataGenerator.int(min_val, max_val))

                if expr.startswith('float['):
                    params = expr[6:-1].split(',')
                    min_val = float(params[0].strip())
                    max_val = float(params[1].strip())
                    decimal = int(params[2].strip()) if len(params) > 2 else 2
                    return str(RandomDataGenerator.float(min_val, max_val, decimal))

                if expr.startswith('date['):
                    params = expr[5:-1].split(',')
                    fmt = params[0].strip().strip('"\'')
                    start = params[1].strip().strip('"\'') if len(params) > 1 else "-30y"
                    end = params[2].strip().strip('"\'') if len(params) > 2 else "today"
                    return RandomDataGenerator.date(start, end, fmt)

                if expr == 'now' or expr.startswith('now['):
                    # 处理 ${now} 或 ${now[%Y-%m-%d]} 格式
                    try:
                        if expr == 'now':
                            return RandomDataGenerator.now()
                        else:
                            fmt = expr[4:-1].strip().strip('"\'')
                            return RandomDataGenerator.now(fmt)
                    except Exception as e:
                        print(f"Error processing now tag: {e}")
                        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if expr.startswith('text['):
                    length = int(expr[5:-1])
                    return RandomDataGenerator.text(length)

                return match.group(0)
            except Exception as e:
                print(f"Error processing random tag {match.group(0)}: {e}")
                return match.group(0)

        return re.sub(r'\$\{\s*([^{}\s]+)\s*\}', replace_random, template)


if __name__ == '__main__':
    print(RandomDataGenerator.email())
    print(RandomDataGenerator.id_card())
    print(RandomDataGenerator.date())
    print(RandomDataGenerator.now())
