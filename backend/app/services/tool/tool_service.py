#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  通用工具集业务逻辑服务层
              提供编码/解码、格式转换、加密/解密、文本处理等功能
"""

import base64
import hashlib
import hmac
import json
import re
from datetime import datetime
from urllib.parse import quote, unquote
from typing import Dict, Any, Optional

import jwt
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import xml.etree.ElementTree as ET


class ToolService:
    """通用工具集业务服务类"""

    # ==================== 编码/解码工具 ====================

    @staticmethod
    def url_encode(text: str) -> Dict[str, Any]:
        """
        URL编码
        
        Args:
            text: 待编码的文本
            
        Returns:
            dict: 包含编码结果的字典
        """
        try:
            encoded = quote(text, safe='')
            return {'success': True, 'result': encoded}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def url_decode(text: str) -> Dict[str, Any]:
        """
        URL解码
        
        Args:
            text: 待解码的文本
            
        Returns:
            dict: 包含解码结果的字典
        """
        try:
            decoded = unquote(text)
            return {'success': True, 'result': decoded}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def base64_encode(text: str) -> Dict[str, Any]:
        """
        Base64编码
        
        Args:
            text: 待编码的文本
            
        Returns:
            dict: 包含编码结果的字典
        """
        try:
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            return {'success': True, 'result': encoded}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def base64_decode(text: str) -> Dict[str, Any]:
        """
        Base64解码
        
        Args:
            text: 待解码的文本
            
        Returns:
            dict: 包含解码结果的字典
        """
        try:
            decoded = base64.b64decode(text).decode('utf-8')
            return {'success': True, 'result': decoded}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def jwt_decode(token: str, secret: Optional[str] = None, verify: bool = True) -> Dict[str, Any]:
        """
        JWT Token解析
        
        Args:
            token: JWT token字符串
            secret: 密钥（可选，用于验证）
            verify: 是否验证签名
            
        Returns:
            dict: 包含解析结果的字典
        """
        try:
            if verify and secret:
                decoded = jwt.decode(token, secret, algorithms=['HS256', 'HS384', 'HS512', 'RS256'])
                return {'success': True, 'result': decoded, 'verified': True}
            else:
                # 不验证签名，直接解析
                decoded = jwt.decode(token, options={"verify_signature": False})
                return {'success': True, 'result': decoded, 'verified': False}
        except jwt.ExpiredSignatureError:
            return {'success': False, 'error': 'Token已过期'}
        except jwt.InvalidTokenError as e:
            return {'success': False, 'error': f'Token无效: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== 格式转换工具 ====================

    @staticmethod
    def json_format(json_text: str, indent: int = 2) -> Dict[str, Any]:
        """
        JSON格式化
        
        Args:
            json_text: JSON字符串
            indent: 缩进空格数
            
        Returns:
            dict: 包含格式化结果的字典
        """
        try:
            obj = json.loads(json_text)
            formatted = json.dumps(obj, ensure_ascii=False, indent=indent)
            return {'success': True, 'result': formatted}
        except json.JSONDecodeError as e:
            return {'success': False, 'error': f'JSON格式错误: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def json_compact(json_text: str) -> Dict[str, Any]:
        """
        JSON压缩（移除所有空白字符）
        
        Args:
            json_text: JSON字符串
            
        Returns:
            dict: 包含压缩结果的字典
        """
        try:
            obj = json.loads(json_text)
            compact = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
            return {'success': True, 'result': compact}
        except json.JSONDecodeError as e:
            return {'success': False, 'error': f'JSON格式错误: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def xml_to_json(xml_text: str) -> Dict[str, Any]:
        """
        XML转JSON
        
        Args:
            xml_text: XML字符串
            
        Returns:
            dict: 包含转换结果的字典
        """
        try:
            root = ET.fromstring(xml_text)
            
            def xml_to_dict(element):
                """递归将XML元素转换为字典"""
                result = {}
                
                # 添加属性
                if element.attrib:
                    result['@attributes'] = element.attrib
                
                # 添加文本内容
                if element.text and element.text.strip():
                    if len(element) == 0:  # 叶子节点
                        result['#text'] = element.text.strip()
                    else:
                        result['#text'] = element.text.strip()
                
                # 处理子元素
                for child in element:
                    child_dict = xml_to_dict(child)
                    if child.tag in result:
                        # 如果标签已存在，转换为列表
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_dict)
                    else:
                        result[child.tag] = child_dict
                
                return result
            
            json_obj = xml_to_dict(root)
            json_str = json.dumps(json_obj, ensure_ascii=False, indent=2)
            return {'success': True, 'result': json_str}
        except ET.ParseError as e:
            return {'success': False, 'error': f'XML解析错误: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def timestamp_to_datetime(timestamp: int, format_str: str = '%Y-%m-%d %H:%M:%S') -> Dict[str, Any]:
        """
        时间戳转日期时间
        
        Args:
            timestamp: Unix时间戳（支持秒和毫秒）
            format_str: 日期格式字符串
            
        Returns:
            dict: 包含转换结果的字典
        """
        try:
            # 判断是秒还是毫秒时间戳
            if timestamp > 1e10:
                timestamp = timestamp / 1000
            dt = datetime.fromtimestamp(timestamp)
            formatted = dt.strftime(format_str)
            return {
                'success': True,
                'result': formatted,
                'timestamp': timestamp,
                'datetime': dt.isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def datetime_to_timestamp(datetime_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> Dict[str, Any]:
        """
        日期时间转时间戳
        
        Args:
            datetime_str: 日期时间字符串
            format_str: 日期格式字符串
            
        Returns:
            dict: 包含转换结果的字典
        """
        try:
            dt = datetime.strptime(datetime_str, format_str)
            timestamp = int(dt.timestamp())
            return {
                'success': True,
                'result': timestamp,
                'datetime': dt.isoformat()
            }
        except ValueError as e:
            return {'success': False, 'error': f'日期格式错误: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== 加密/解密工具 ====================

    @staticmethod
    def md5_hash(text: str) -> Dict[str, Any]:
        """
        MD5哈希
        
        Args:
            text: 待哈希的文本
            
        Returns:
            dict: 包含哈希结果的字典
        """
        try:
            md5_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            return {'success': True, 'result': md5_hash}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def sha1_hash(text: str) -> Dict[str, Any]:
        """SHA1哈希"""
        try:
            sha1_hash = hashlib.sha1(text.encode('utf-8')).hexdigest()
            return {'success': True, 'result': sha1_hash}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def sha256_hash(text: str) -> Dict[str, Any]:
        """SHA256哈希"""
        try:
            sha256_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            return {'success': True, 'result': sha256_hash}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def sha512_hash(text: str) -> Dict[str, Any]:
        """SHA512哈希"""
        try:
            sha512_hash = hashlib.sha512(text.encode('utf-8')).hexdigest()
            return {'success': True, 'result': sha512_hash}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def hmac_hash(text: str, key: str, algorithm: str = 'sha256') -> Dict[str, Any]:
        """
        HMAC哈希
        
        Args:
            text: 待哈希的文本
            key: 密钥
            algorithm: 算法 ('md5', 'sha1', 'sha256', 'sha512')
            
        Returns:
            dict: 包含哈希结果的字典
        """
        try:
            alg_map = {
                'md5': hashlib.md5,
                'sha1': hashlib.sha1,
                'sha256': hashlib.sha256,
                'sha512': hashlib.sha512
            }
            if algorithm not in alg_map:
                return {'success': False, 'error': f'不支持的算法: {algorithm}'}
            
            hash_obj = hmac.new(key.encode('utf-8'), text.encode('utf-8'), alg_map[algorithm])
            result = hash_obj.hexdigest()
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def aes_encrypt(plaintext: str, key: str, mode: str = 'CBC') -> Dict[str, Any]:
        """
        AES加密
        
        Args:
            plaintext: 明文
            key: 密钥（16/24/32字节）
            mode: 加密模式 ('CBC', 'ECB')
            
        Returns:
            dict: 包含加密结果的字典（base64编码）
        """
        try:
            # 确保密钥长度为16、24或32字节
            key_bytes = key.encode('utf-8')[:32]
            if len(key_bytes) < 16:
                key_bytes = key_bytes.ljust(16, b'0')
            elif len(key_bytes) < 24:
                key_bytes = key_bytes.ljust(24, b'0')
            else:
                key_bytes = key_bytes[:32]
            
            plaintext_bytes = plaintext.encode('utf-8')
            
            if mode.upper() == 'CBC':
                # CBC模式需要IV
                iv = get_random_bytes(16)
                cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
                padded = pad(plaintext_bytes, AES.block_size)
                ciphertext = cipher.encrypt(padded)
                # 将IV和密文组合，base64编码
                result = base64.b64encode(iv + ciphertext).decode('utf-8')
            else:  # ECB模式
                cipher = AES.new(key_bytes, AES.MODE_ECB)
                padded = pad(plaintext_bytes, AES.block_size)
                ciphertext = cipher.encrypt(padded)
                result = base64.b64encode(ciphertext).decode('utf-8')
            
            return {'success': True, 'result': result, 'mode': mode}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def aes_decrypt(ciphertext: str, key: str, mode: str = 'CBC') -> Dict[str, Any]:
        """
        AES解密
        
        Args:
            ciphertext: 密文（base64编码）
            key: 密钥（16/24/32字节）
            mode: 加密模式 ('CBC', 'ECB')
            
        Returns:
            dict: 包含解密结果的字典
        """
        try:
            # 确保密钥长度为16、24或32字节
            key_bytes = key.encode('utf-8')[:32]
            if len(key_bytes) < 16:
                key_bytes = key_bytes.ljust(16, b'0')
            elif len(key_bytes) < 24:
                key_bytes = key_bytes.ljust(24, b'0')
            else:
                key_bytes = key_bytes[:32]
            
            ciphertext_bytes = base64.b64decode(ciphertext)
            
            if mode.upper() == 'CBC':
                # 提取IV和密文
                iv = ciphertext_bytes[:16]
                ciphertext_only = ciphertext_bytes[16:]
                cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
                padded = cipher.decrypt(ciphertext_only)
                plaintext = unpad(padded, AES.block_size).decode('utf-8')
            else:  # ECB模式
                cipher = AES.new(key_bytes, AES.MODE_ECB)
                padded = cipher.decrypt(ciphertext_bytes)
                plaintext = unpad(padded, AES.block_size).decode('utf-8')
            
            return {'success': True, 'result': plaintext}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def rsa_encrypt(plaintext: str, public_key: str) -> Dict[str, Any]:
        """
        RSA加密
        
        Args:
            plaintext: 明文
            public_key: 公钥（PEM格式）
            
        Returns:
            dict: 包含加密结果的字典（base64编码）
        """
        try:
            key = RSA.import_key(public_key)
            cipher = PKCS1_v1_5.new(key)
            ciphertext = cipher.encrypt(plaintext.encode('utf-8'))
            if ciphertext is None:
                return {'success': False, 'error': '加密失败，可能是密钥不匹配'}
            result = base64.b64encode(ciphertext).decode('utf-8')
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def rsa_decrypt(ciphertext: str, private_key: str) -> Dict[str, Any]:
        """
        RSA解密
        
        Args:
            ciphertext: 密文（base64编码）
            private_key: 私钥（PEM格式）
            
        Returns:
            dict: 包含解密结果的字典
        """
        try:
            key = RSA.import_key(private_key)
            cipher = PKCS1_v1_5.new(key)
            ciphertext_bytes = base64.b64decode(ciphertext)
            plaintext = cipher.decrypt(ciphertext_bytes, None)
            if plaintext is None:
                return {'success': False, 'error': '解密失败，可能是密钥不匹配'}
            result = plaintext.decode('utf-8')
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== 文本处理工具 ====================

    @staticmethod
    def regex_test(text: str, pattern: str, flags: int = 0) -> Dict[str, Any]:
        """
        正则表达式测试
        
        Args:
            text: 待匹配的文本
            pattern: 正则表达式模式
            flags: 正则标志（如 re.IGNORECASE, re.MULTILINE）
            
        Returns:
            dict: 包含匹配结果的字典
        """
        try:
            regex = re.compile(pattern, flags)
            matches = regex.finditer(text)
            
            match_results = []
            for match in matches:
                match_results.append({
                    'match': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'groups': match.groups()
                })
            
            # 测试是否匹配
            full_match = regex.fullmatch(text)
            is_full_match = full_match is not None
            
            # 查找第一个匹配
            first_match = regex.search(text)
            
            return {
                'success': True,
                'matches': match_results,
                'match_count': len(match_results),
                'is_full_match': is_full_match,
                'first_match': {
                    'match': first_match.group() if first_match else None,
                    'start': first_match.start() if first_match else None,
                    'end': first_match.end() if first_match else None
                }
            }
        except re.error as e:
            return {'success': False, 'error': f'正则表达式错误: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def text_compare(text1: str, text2: str, ignore_case: bool = False, ignore_whitespace: bool = False) -> Dict[str, Any]:
        """
        文本对比
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            ignore_case: 是否忽略大小写
            ignore_whitespace: 是否忽略空白字符
            
        Returns:
            dict: 包含对比结果的字典
        """
        try:
            processed_text1 = text1
            processed_text2 = text2
            
            if ignore_case:
                processed_text1 = processed_text1.lower()
                processed_text2 = processed_text2.lower()
            
            if ignore_whitespace:
                processed_text1 = re.sub(r'\s+', '', processed_text1)
                processed_text2 = re.sub(r'\s+', '', processed_text2)
            
            is_equal = processed_text1 == processed_text2
            diff_length = abs(len(processed_text1) - len(processed_text2))
            
            # 计算相似度（简单的字符匹配度）
            if len(processed_text1) == 0 and len(processed_text2) == 0:
                similarity = 1.0
            elif len(processed_text1) == 0 or len(processed_text2) == 0:
                similarity = 0.0
            else:
                # 使用最长公共子序列的简单计算
                max_len = max(len(processed_text1), len(processed_text2))
                common_chars = sum(1 for a, b in zip(processed_text1, processed_text2) if a == b)
                similarity = common_chars / max_len if max_len > 0 else 0.0
            
            return {
                'success': True,
                'is_equal': is_equal,
                'similarity': round(similarity, 4),
                'length_diff': diff_length,
                'text1_length': len(text1),
                'text2_length': len(text2),
                'processed_text1_length': len(processed_text1),
                'processed_text2_length': len(processed_text2)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


# 创建单例服务实例
tool_service = ToolService()

