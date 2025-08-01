#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  通用工具集路由
"""

from flask import Blueprint, request, jsonify

from ...services.tool.tool_service import ToolService

tool_bp = Blueprint('tool', __name__)


# ==================== 编码/解码工具 ====================

@tool_bp.route('/tools/url/encode', methods=['POST'])
def url_encode():
    """URL编码"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'success': False, 'message': '文本不能为空'}), 400
        result = ToolService.url_encode(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/url/decode', methods=['POST'])
def url_decode():
    """URL解码"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'success': False, 'message': '文本不能为空'}), 400
        result = ToolService.url_decode(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/base64/encode', methods=['POST'])
def base64_encode():
    """Base64编码"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'success': False, 'message': '文本不能为空'}), 400
        result = ToolService.base64_encode(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/base64/decode', methods=['POST'])
def base64_decode():
    """Base64解码"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'success': False, 'message': '文本不能为空'}), 400
        result = ToolService.base64_decode(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/jwt/decode', methods=['POST'])
def jwt_decode():
    """JWT Token解析"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        secret = data.get('secret', None)
        verify = data.get('verify', True)
        
        if not token:
            return jsonify({'success': False, 'message': 'Token不能为空'}), 400
        
        result = ToolService.jwt_decode(token, secret, verify)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 格式转换工具 ====================

@tool_bp.route('/tools/json/format', methods=['POST'])
def json_format():
    """JSON格式化"""
    try:
        data = request.get_json()
        json_text = data.get('json', '')
        indent = data.get('indent', 2)
        
        if not json_text:
            return jsonify({'success': False, 'message': 'JSON文本不能为空'}), 400
        
        result = ToolService.json_format(json_text, indent)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/json/compact', methods=['POST'])
def json_compact():
    """JSON压缩"""
    try:
        data = request.get_json()
        json_text = data.get('json', '')
        
        if not json_text:
            return jsonify({'success': False, 'message': 'JSON文本不能为空'}), 400
        
        result = ToolService.json_compact(json_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/xml/to-json', methods=['POST'])
def xml_to_json():
    """XML转JSON"""
    try:
        data = request.get_json()
        xml_text = data.get('xml', '')
        
        if not xml_text:
            return jsonify({'success': False, 'message': 'XML文本不能为空'}), 400
        
        result = ToolService.xml_to_json(xml_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/timestamp/to-datetime', methods=['POST'])
def timestamp_to_datetime():
    """时间戳转日期时间"""
    try:
        data = request.get_json()
        timestamp = data.get('timestamp')
        format_str = data.get('format', '%Y-%m-%d %H:%M:%S')
        
        if timestamp is None:
            return jsonify({'success': False, 'message': '时间戳不能为空'}), 400
        
        result = ToolService.timestamp_to_datetime(int(timestamp), format_str)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/datetime/to-timestamp', methods=['POST'])
def datetime_to_timestamp():
    """日期时间转时间戳"""
    try:
        data = request.get_json()
        datetime_str = data.get('datetime', '')
        format_str = data.get('format', '%Y-%m-%d %H:%M:%S')
        
        if not datetime_str:
            return jsonify({'success': False, 'message': '日期时间不能为空'}), 400
        
        result = ToolService.datetime_to_timestamp(datetime_str, format_str)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 加密/解密工具 ====================

@tool_bp.route('/tools/hash/md5', methods=['POST'])
def md5_hash():
    """MD5哈希"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'message': '文本不能为空'}), 400
        
        result = ToolService.md5_hash(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/hash/sha1', methods=['POST'])
def sha1_hash():
    """SHA1哈希"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'message': '文本不能为空'}), 400
        
        result = ToolService.sha1_hash(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/hash/sha256', methods=['POST'])
def sha256_hash():
    """SHA256哈希"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'message': '文本不能为空'}), 400
        
        result = ToolService.sha256_hash(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/hash/sha512', methods=['POST'])
def sha512_hash():
    """SHA512哈希"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'message': '文本不能为空'}), 400
        
        result = ToolService.sha512_hash(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/hash/hmac', methods=['POST'])
def hmac_hash():
    """HMAC哈希"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        key = data.get('key', '')
        algorithm = data.get('algorithm', 'sha256')
        
        if not text:
            return jsonify({'success': False, 'message': '文本不能为空'}), 400
        if not key:
            return jsonify({'success': False, 'message': '密钥不能为空'}), 400
        
        result = ToolService.hmac_hash(text, key, algorithm)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/aes/encrypt', methods=['POST'])
def aes_encrypt():
    """AES加密"""
    try:
        data = request.get_json()
        plaintext = data.get('text', '')
        key = data.get('key', '')
        mode = data.get('mode', 'CBC')
        
        if not plaintext:
            return jsonify({'success': False, 'message': '明文不能为空'}), 400
        if not key:
            return jsonify({'success': False, 'message': '密钥不能为空'}), 400
        
        result = ToolService.aes_encrypt(plaintext, key, mode)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/aes/decrypt', methods=['POST'])
def aes_decrypt():
    """AES解密"""
    try:
        data = request.get_json()
        ciphertext = data.get('text', '')
        key = data.get('key', '')
        mode = data.get('mode', 'CBC')
        
        if not ciphertext:
            return jsonify({'success': False, 'message': '密文不能为空'}), 400
        if not key:
            return jsonify({'success': False, 'message': '密钥不能为空'}), 400
        
        result = ToolService.aes_decrypt(ciphertext, key, mode)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/rsa/encrypt', methods=['POST'])
def rsa_encrypt():
    """RSA加密"""
    try:
        data = request.get_json()
        plaintext = data.get('text', '')
        public_key = data.get('public_key', '')
        
        if not plaintext:
            return jsonify({'success': False, 'message': '明文不能为空'}), 400
        if not public_key:
            return jsonify({'success': False, 'message': '公钥不能为空'}), 400
        
        result = ToolService.rsa_encrypt(plaintext, public_key)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/rsa/decrypt', methods=['POST'])
def rsa_decrypt():
    """RSA解密"""
    try:
        data = request.get_json()
        ciphertext = data.get('text', '')
        private_key = data.get('private_key', '')
        
        if not ciphertext:
            return jsonify({'success': False, 'message': '密文不能为空'}), 400
        if not private_key:
            return jsonify({'success': False, 'message': '私钥不能为空'}), 400
        
        result = ToolService.rsa_decrypt(ciphertext, private_key)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 文本处理工具 ====================

@tool_bp.route('/tools/regex/test', methods=['POST'])
def regex_test():
    """正则表达式测试"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        pattern = data.get('pattern', '')
        flags = data.get('flags', 0)
        
        if not pattern:
            return jsonify({'success': False, 'message': '正则表达式不能为空'}), 400
        
        result = ToolService.regex_test(text, pattern, flags)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@tool_bp.route('/tools/text/compare', methods=['POST'])
def text_compare():
    """文本对比"""
    try:
        data = request.get_json()
        text1 = data.get('text1', '')
        text2 = data.get('text2', '')
        ignore_case = data.get('ignore_case', False)
        ignore_whitespace = data.get('ignore_whitespace', False)
        
        result = ToolService.text_compare(text1, text2, ignore_case, ignore_whitespace)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

