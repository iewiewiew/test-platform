#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author       weimenghua
@time         2023/9/21 18:31
@description  HTTP 请求工具类
"""

import os
import ssl
import json
import string
import urllib3
import inspect
import random
import http.client
from datetime import datetime
from urllib.parse import urlencode, urlparse

from .log_util import Logger
from .path_util import PathUtils

urllib3.disable_warnings()

logger = Logger()


class HttpClient:

    def __init__(self, host, use_https=True):
        self.headers = None
        self.host = host
        self.cookie = None
        self.conn = None
        self.use_https = use_https
        self.timeout = 30

    def __del__(self):
        """析构函数，确保连接关闭"""
        if self.conn:
            self.conn.close()

    def convert_gitee_url(self, path):
        if (self.host == "api.gitee.com" or self.host == "go-api.gitee.com") and path.startswith("/go-api"):
            host = "go-api.gitee.com"
            path = path[len("/go-api"):]
            logger.info(f"转换后的请求 ------ {host} {path}")
            return host, path
        elif self.host == "go-api.gitee.com" and not path.startswith("/go-api"):
            host = "api.gitee.com"
            path = path
            logger.info(f"转换后的请求 ------ {host} {path}")
            return host, path
        host = self.host
        return host, path

    def get_caller_info(self):
        """
        获取调用方的函数名称和 docstring。
        返回一个字典，包含 caller_name 和 caller_docstring。
        """
        # 获取当前调用栈
        stack = inspect.stack()

        # 确保调用栈至少有3层（当前函数、直接调用者、调用方）
        if len(stack) > 2:
            caller_frame = stack[2]  # 调用方的栈帧
            caller_function_name = caller_frame.function  # 调用方的函数名称

            # 获取调用方所在的模块
            module = inspect.getmodule(caller_frame[0])

            # 如果调用方是类方法
            if 'self' in caller_frame.frame.f_locals:
                # 从调用方栈帧的局部变量中获取类实例
                cls_instance = caller_frame.frame.f_locals['self']
                cls = cls_instance.__class__  # 获取类对象
                # 从类中获取方法对象
                method = getattr(cls, caller_function_name, None)
                if method:
                    return {
                        "caller_name": f"{cls.__name__}.{caller_function_name}",
                        "caller_docstring": inspect.getdoc(method) or "No docstring available"
                    }

            # 如果调用方是普通函数
            elif module:
                # 从模块中获取函数对象
                func = getattr(module, caller_function_name, None)
                if func:
                    # 如果模块是 __main__，省略模块名
                    module_name = "" if module.__name__ == "__main__" else module.__name__
                    if module_name:
                        caller_name = f"{module_name}.{caller_function_name}"
                    else:
                        caller_name = caller_function_name
                    return {
                        "caller_name": caller_name,
                        "caller_docstring": inspect.getdoc(func) or "No docstring available"
                    }

        # 如果无法正确获取信息，则返回默认值
        return {
            "caller_name": "Unknown",
            "caller_docstring": "No docstring available"
        }

    def build_curl_command(self, method, path, headers=None, body=None):
        # 构建基础的 curl 命令
        curl_command = f"curl -X {method} 'https://{self.conn.host}{path}'"

        # 处理请求体
        if body:
            if isinstance(body, dict):
                body_str = json.dumps(body)
            else:
                body_str = str(body)
            curl_command += f" -d '{body_str}'"

        # 处理头部
        if headers:
            header_str = " ".join([f"-H '{k}: {v}'" for k, v in headers.items()])
            curl_command += f" {header_str}"

        return curl_command

    def create_connection(self, host):
        if self.conn:
            self.conn.close()  # 关闭之前的连接

        attempts = [self.use_https, not self.use_https]
        failed_attempts = []  # 记录所有失败的尝试信息
        
        for attempt in attempts:
            try:
                if attempt:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    self.conn = http.client.HTTPSConnection(host, context=context)
                    protocol = "HTTPS"
                    logger.info(f"尝试使用 HTTPS 连接到 {host}")
                else:
                    self.conn = http.client.HTTPConnection(host)
                    protocol = "HTTP"
                    logger.info(f"尝试使用 HTTP 连接到 {host}")

                # 尝试发送 HEAD 请求以测试连接
                self.conn.request("HEAD", "/")
                response = self.conn.getresponse()
                response.read()  # 读取响应以清理连接状态
                logger.info(f"使用 {protocol} 连接成功！")
                return  # 连接成功，退出方法

            except Exception as e:
                # 将单次尝试失败记录为 DEBUG 级别，避免成功时还看到错误日志
                protocol = "HTTPS" if attempt else "HTTP"
                logger.debug(f"尝试使用 {protocol} 连接失败: {e}")
                failed_attempts.append(f"{protocol}: {e}")
                if self.conn:
                    self.conn.close()  # 关闭连接

        # 只有所有尝试都失败时才输出 ERROR 日志
        error_msg = f"HTTP 和 HTTPS 连接均失败: {', '.join(failed_attempts)}"
        logger.error(error_msg)
        raise Exception(error_msg)

    def send_get_request(self, path, headers={}):
        """Get 请求"""
        request_type = "GET"

        caller_info = self.get_caller_info()

        host, path = self.convert_gitee_url(path)

        # 更新主机并创建新的连接
        self.host = host
        self.create_connection(self.host)

        self.conn.request("GET", path, headers=headers)
        self.conn.timeout = 10
        response = self.conn.getresponse()
        response_status = response.getcode()
        response_data = response.read().decode("utf-8")

        self.conn.close()

        body = None

        if response_status in (200, 201, 204):
            logger.info(f"【请求方法】{caller_info['caller_name']}")
            logger.info(f"【用例名称】{caller_info['caller_docstring']}")
            logger.info(f"【请求地址】https://{self.host}{path}")
            logger.info(f"【请求方式】{request_type}")
            logger.info(f"【请求参数】{body}")
            logger.info(f"【响应状态】{response_status}")
            logger.info(f"【响应结果】{response_data}")
        else:
            logger.error(f"【请求方法】{caller_info['caller_name']}")
            logger.error(f"【用例名称】{caller_info['caller_docstring']}")
            logger.error(f"【请求地址】https://{self.host}{path}")
            logger.error(f"【请求方式】{request_type}")
            logger.error(f"【请求参数】{body}")
            logger.error(f"【响应状态】{response_status}")
            logger.error(f"【响应结果】{response_data}")

        self.save_response_data(response_data, caller_info['caller_name'], path=None)

        curl_command = self.build_curl_command('GET', path, headers)
        logger.info(f"【命令行】{curl_command}")
        logger.debug("-----------------------------------------------------------------------")

        return {
            'status': response_status,
            'data': response_data
        }

    def send_post_request(self, path, body, headers=None):
        """POST 请求"""
        request_type = "POST"

        caller_info = self.get_caller_info()

        host, path = self.convert_gitee_url(path)

        # 更新主机并创建新的连接
        self.host = host
        self.create_connection(self.host)

        # 根据请求头判断数据类型
        content_type = headers.get("Content-Type", "").lower()
        if "application/json" in content_type:
            body = json.dumps(body)
            # body = body.encode('utf-8')
        elif "application/x-www-form-urlencoded" in content_type:
            body = urlencode(body).encode('utf-8')
        else:
            raise ValueError("Unsupported Content-Type in headers.")
        self.conn.request("POST", path, body, headers)
        response = self.conn.getresponse()
        response_status = response.getcode()
        response_data = response.read().decode("utf-8")
        self.conn.close()

        if response_status in (200, 201, 204):
            logger.info(f"【请求方法】{caller_info['caller_name']}")
            logger.info(f"【用例名称】{caller_info['caller_docstring']}")
            logger.info(f"【请求地址】https://{self.host}{path}")
            logger.info(f"【请求方式】{request_type}")
            logger.info(f"【请求参数】{body}")
            logger.info(f"【响应状态】{response_status}")
            logger.info(f"【响应结果】{response_data}")
        else:
            logger.error(f"【请求方法】{caller_info['caller_name']}")
            logger.error(f"【用例名称】{caller_info['caller_docstring']}")
            logger.error(f"【请求地址】https://{self.host}{path}")
            logger.error(f"【请求方式】{request_type}")
            logger.error(f"【请求参数】{body}")
            logger.error(f"【响应状态】{response_status}")
            logger.error(f"【响应结果】{response_data}")

        self.save_response_data(response_data, caller_info['caller_name'], path=None)

        curl_command = self.build_curl_command('POST', path, headers, body)
        logger.info(f"【命令行】{curl_command}")
        logger.debug("-----------------------------------------------------------------------")

        response_header = response.headers
        return {
            'status': response_status,
            'data': response_data,
            'header': response_header
        }

    # @method_decorator
    def send_put_request(self, path, body, headers=None):
        """PUT 请求"""
        request_type = "PUT"

        caller_info = self.get_caller_info()

        host, path = self.convert_gitee_url(path)

        # 更新主机并创建新的连接
        self.host = host
        self.create_connection(self.host)

        # 根据请求头判断数据类型
        content_type = headers.get("Content-Type", "").lower()
        if "application/json" in content_type:
            if isinstance(body, dict):
                # 如果是字典，转换为 JSON 字符串
                body = json.dumps(body, ensure_ascii=False)
                # body = body.encode('utf-8')
        elif "application/x-www-form-urlencoded" in content_type:
            body = urlencode(body)
        else:
            raise ValueError("Unsupported Content-Type in headers.")
        if body:
            body = body.encode('utf-8')
        self.conn.request("PUT", path, body, headers)
        response = self.conn.getresponse()
        response_status = response.getcode()
        response_data = response.read().decode("utf-8")
        self.conn.close()

        if response_status in (200, 201, 204):
            logger.info(f"【请求方法】{caller_info['caller_name']}")
            logger.info(f"【用例名称】{caller_info['caller_docstring']}")
            logger.info(f"【请求地址】https://{self.host}{path}")
            logger.info(f"【请求方式】{request_type}")
            logger.info(f"【请求参数】{body}")
            logger.info(f"【响应状态】{response_status}")
            logger.info(f"【响应结果】{response_data}")
        else:
            logger.error(f"【请求方法】{caller_info['caller_name']}")
            logger.error(f"【用例名称】{caller_info['caller_docstring']}")
            logger.error(f"【请求地址】https://{self.host}{path}")
            logger.error(f"【请求方式】{request_type}")
            logger.error(f"【请求参数】{body}")
            logger.error(f"【响应状态】{response_status}")
            logger.error(f"【响应结果】{response_data}")

        self.save_response_data(response_data, caller_info['caller_name'], path=None)

        curl_command = self.build_curl_command('PUT', path, headers, body)
        logger.info(f"【命令行】{curl_command}")
        logger.debug("-----------------------------------------------------------------------")

        return {
            'status': response_status,
            'data': response_data
        }

    def send_patch_request(self, path, body, headers=None):
        """PATCH 请求"""
        request_type = "PATCH"

        caller_info = self.get_caller_info()

        host, path = self.convert_gitee_url(path)

        # 更新主机并创建新的连接
        self.host = host
        self.create_connection(self.host)

        # 根据请求头判断数据类型
        content_type = headers.get("Content-Type", "").lower()
        if "application/json" in content_type:
            body = json.dumps(body)
        elif "application/x-www-form-urlencoded" in content_type:
            body = urlencode(body)
        else:
            raise ValueError("Unsupported Content-Type in headers.")
        self.conn.request("PATCH", path, body, headers)
        response = self.conn.getresponse()
        response_status = response.getcode()
        response_data = response.read().decode("utf-8")
        self.conn.close()

        if response_status in (200, 201, 204):
            logger.info(f"【请求方法】{caller_info['caller_name']}")
            logger.info(f"【用例名称】{caller_info['caller_docstring']}")
            logger.info(f"【请求地址】https://{self.host}{path}")
            logger.info(f"【请求方式】{request_type}")
            logger.info(f"【请求参数】{body}")
            logger.info(f"【响应状态】{response_status}")
            logger.info(f"【响应结果】{response_data}")
        else:
            logger.error(f"【请求方法】{caller_info['caller_name']}")
            logger.error(f"【用例名称】{caller_info['caller_docstring']}")
            logger.error(f"【请求地址】https://{self.host}{path}")
            logger.error(f"【请求方式】{request_type}")
            logger.error(f"【请求参数】{body}")
            logger.error(f"【响应状态】{response_status}")
            logger.error(f"【响应结果】{response_data}")

        self.save_response_data(response_data, caller_info['caller_name'], path=None)

        curl_command = self.build_curl_command('PATCH', path, headers, body)
        logger.info(f"【命令行】{curl_command}")
        logger.debug("-----------------------------------------------------------------------")

        return {
            'status': response_status,
            'data': response_data
        }

    def send_delete_request(self, path, body=None, headers={}):
        """DELETE 请求"""
        request_type = "DELETE"

        caller_info = self.get_caller_info()

        host, path = self.convert_gitee_url(path)

        # 更新主机并创建新的连接
        self.host = host
        self.create_connection(self.host)

        if body is not None:
            if isinstance(body, str):
                body = body.encode('utf-8')  # 转换为字节串
            elif isinstance(body, dict):
                body = json.dumps(body).encode('utf-8')  # JSON 转换为字节串

        self.conn.request("DELETE", path, body=body, headers=headers)
        response = self.conn.getresponse()
        response_status = response.getcode()
        response_data = response.read().decode("utf-8")
        self.conn.close()

        if response_status in (200, 201, 204):
            logger.info(f"【请求方法】{caller_info['caller_name']}")
            logger.info(f"【用例名称】{caller_info['caller_docstring']}")
            logger.info(f"【请求地址】https://{self.host}{path}")
            logger.info(f"【请求方式】{request_type}")
            logger.info(f"【请求参数】{body}")
            logger.info(f"【响应状态】{response_status}")
            logger.info(f"【响应结果】{response_data}")
        else:
            logger.error(f"【请求方法】{caller_info['caller_name']}")
            logger.error(f"【用例名称】{caller_info['caller_docstring']}")
            logger.error(f"【请求地址】https://{self.host}{path}")
            logger.error(f"【请求方式】{request_type}")
            logger.error(f"【请求参数】{body}")
            logger.error(f"【响应状态】{response_status}")
            logger.error(f"【响应结果】{response_data}")

        self.save_response_data(response_data, caller_info['caller_name'], path=None)

        curl_command = self.build_curl_command('DELETE', path, headers, body)
        logger.info(f"【命令行】{curl_command}")
        logger.debug("-----------------------------------------------------------------------")

        return {
            'status': response_status,
            'data': response_data
        }

    def save_response_data(self, response_data, method_name, path=None):
        base_path = PathUtils.get_project_root_path('test-platform')
        # base_path = PathUtils.get_project_root_path('Learn-Python')
        time = datetime.now().strftime('%Y%m%d')
        path = base_path + f"/backend/app/autotest/report/log/{time}/"

        if not os.path.exists(path):
            os.makedirs(path)
            logger.info("路径 {} 不存在，已创建".format(path))

        try:
            # 将响应数据解析为JSON
            json_data = json.loads(response_data)
            # 将JSON数据写入文件
            with open(path + "{}_response.json".format(method_name), "w") as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)
            logger.info("【响应文件】{}{}_response.json".format(path, method_name))
        except json.JSONDecodeError:
            with open(path + "{}_response.txt".format(method_name), "w") as file:
                # file.write(response_data.decode())
                file.write(response_data)
            logger.info("【响应文件】{}{}_response.txt".format(path, method_name))

    def upload_file(self, path, file_path, form_data=None, headers=None):
        """
        上传文件方法，支持multipart/form-data格式

        Args:
            path: 上传接口路径
            file_path: 要上传的文件路径
            form_data: 其他表单数据(dict)
            headers: 自定义请求头

        Returns:
            上传接口的响应结果
        """
        caller_info = self.get_caller_info()

        # 处理主机和路径转换
        host, path = self.convert_gitee_url(path)
        self.host = host
        self.create_connection(self.host)

        # 准备multipart边界
        boundary = '----WebKitFormBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        # 保存原始headers
        original_headers = getattr(self, 'headers', {})

        upload_headers = dict(self.headers) if self.headers is not None else {}
        if headers is not None:
            upload_headers.update(headers)
        upload_headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'

        # 准备请求体
        body = []

        # 添加表单数据
        if form_data:
            for key, value in form_data.items():
                body.append(f'--{boundary}\r\n'.encode('utf-8'))
                body.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode('utf-8'))
                body.append(f'{value}\r\n'.encode('utf-8'))

        # 添加文件数据
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            file_content = f.read()

        body.append(f'--{boundary}\r\n'.encode('utf-8'))
        body.append(f'Content-Disposition: form-data; name="files[]"; filename="{file_name}"\r\n'.encode('utf-8'))
        body.append(f'Content-Type: application/octet-stream\r\n\r\n'.encode('utf-8'))
        body.append(file_content)
        body.append(f'\r\n--{boundary}--\r\n'.encode('utf-8'))

        # 发送请求
        self.conn.request("POST", path, body=b''.join(body), headers=upload_headers)
        response = self.conn.getresponse()
        response_status = response.getcode()
        response_data = response.read().decode("utf-8")
        self.conn.close()

        # 记录日志
        if response_status in [200, 201]:
            logger.info(
                f"接口:{caller_info['caller_docstring']} 请求地址: {self.host} "
                f"POST 方法:{caller_info['caller_name']} 请求:{path} "
                f"响应:{response_status} {response_data}"
            )
        else:
            logger.error(
                f"接口:{caller_info['caller_docstring']} 请求地址: {self.host} "
                f"POST 方法:{caller_info['caller_name']} 请求:{path} "
                f"响应:{response_status} {response_data}"
            )

        self.save_response_data(response_data, caller_info['caller_name'], path=None)

        # 恢复原始headers
        if hasattr(self, 'headers'):
            self.headers = original_headers

        return {
            'status': response_status,
            'data': response_data
        }

    def download_file(self, path, save_path=None, headers=None, show_progress=True, max_redirects=5):
        """
        完整的文件下载方法，支持中文路径和自动重定向

        Args:
            path: 文件路径（如 "/private_asset/id?filename=测试.csv"）
            save_path: 保存路径（None=自动生成，目录=自动添加文件名，完整路径=直接使用）
            headers: 自定义请求头
            show_progress: 是否显示进度条
            max_redirects: 最大重定向次数

        Returns:
            文件保存的完整路径

        Raises:
            所有可能的网络和文件操作异常
        """
        # ==================== 1. 参数校验 ====================
        if not isinstance(path, str):
            raise TypeError("path参数必须是字符串")
        if not path.startswith('/'):
            path = '/' + path

        # ==================== 2. URL编码处理 ====================
        def encode_uri_component(s):
            """模拟JavaScript的encodeURIComponent，处理中文等特殊字符"""
            from urllib.parse import quote
            return quote(s.encode('utf-8'), safe="~()*!.'")

        # 解析原始路径
        parsed = urlparse(path)

        # 编码查询参数（特别是filename）
        encoded_query = None
        if parsed.query:
            query_parts = []
            for param in parsed.query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    if key == 'filename':
                        value = encode_uri_component(value)[0]  # 只取编码结果
                    query_parts.append(f"{key}={value}")
                else:
                    query_parts.append(param)
            encoded_query = '&'.join(query_parts)

        # 构建完整编码路径
        full_path = parsed.path
        if encoded_query:
            full_path += f"?{encoded_query}"

        # ==================== 3. 文件名处理 ====================
        def safe_filename(filename):
            """生成安全的文件名，处理中文和特殊字符"""
            import re
            # 保留中文、字母、数字、下划线、短横线和点
            filename = re.sub(r'[\\/*?:"<>|]', "", filename)
            return filename.strip()

        # 从查询参数获取原始文件名
        original_filename = None
        if 'filename=' in parsed.query:
            original_filename = parsed.query.split('filename=')[1].split('&')[0]

        # ==================== 4. 保存路径处理 ====================
        # 确定最终文件名
        final_filename = None
        if original_filename:
            final_filename = safe_filename(original_filename)
        else:
            final_filename = safe_filename(os.path.basename(parsed.path)) or "download"

        # 处理三种save_path情况
        if save_path is None:
            save_path = os.path.join(os.getcwd(), final_filename)
        elif os.path.isdir(save_path):
            save_path = os.path.join(save_path, final_filename)
        else:
            # 已经是完整路径，直接使用
            pass

        # 确保路径是字符串（处理PathLike对象）
        try:
            save_path = str(save_path)
        except UnicodeEncodeError:
            save_path = save_path.encode('utf-8').decode('utf-8')

        # 检查是否是目录
        if os.path.isdir(save_path):
            raise ValueError(f"保存路径不能是目录: {save_path}")

        # ==================== 5. 创建目录 ====================
        dir_path = os.path.dirname(save_path)
        if dir_path:
            try:
                os.makedirs(dir_path, exist_ok=True)
            except (UnicodeEncodeError, OSError) as e:
                # 处理中文目录问题
                try:
                    dir_path = dir_path.encode('utf-8').decode('utf-8')
                    os.makedirs(dir_path, exist_ok=True)
                except Exception as e:
                    raise OSError(f"无法创建目录 {dir_path}: {e}")

        # ==================== 6. 下载核心逻辑 ====================
        redirect_count = 0
        current_host = self.host
        current_path = full_path  # 使用编码后的路径

        while redirect_count <= max_redirects:
            self.conn = None
            try:
                # 建立连接
                self.create_connection(current_host)

                # 发送请求（关键：使用编码后的路径）
                self.conn.request("GET", current_path, headers=headers or {})
                response = self.conn.getresponse()

                # 处理重定向
                if response.status in (301, 302, 303, 307, 308):
                    redirect_count += 1
                    if redirect_count > max_redirects:
                        raise RuntimeError(f"达到最大重定向次数 ({max_redirects})")

                    location = response.getheader('Location')
                    if not location:
                        raise RuntimeError("重定向响应缺少Location头")

                    logger.info(f"重定向 [{redirect_count}/{max_redirects}] => {location}")

                    # 解析新位置
                    new_url = urlparse(location)
                    current_host = new_url.netloc or current_host
                    current_path = new_url.path
                    if new_url.query:
                        current_path += f"?{new_url.query}"

                    continue

                # 检查状态码
                if response.status != 200:
                    raise IOError(f"HTTP {response.status} - {response.reason}")

                # 获取文件大小
                file_size = int(response.getheader('Content-Length', 0))
                downloaded = 0

                # 下载文件
                with open(save_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break

                        f.write(chunk)
                        downloaded += len(chunk)

                        # 显示进度
                        if show_progress and file_size > 0:
                            percent = downloaded / file_size * 100
                            print(f"\r下载进度: {percent:.1f}% ({downloaded}/{file_size} bytes)",
                                  end='', flush=True)

                if show_progress:
                    print()  # 进度条换行

                logger.info(f"文件下载完成: {save_path}")
                return save_path

            except Exception as e:
                # 清理部分下载的文件
                if os.path.exists(save_path):
                    try:
                        os.remove(save_path)
                    except:
                        pass
                raise
            finally:
                if self.conn:
                    self.conn.close()

        raise RuntimeError(f"达到最大重定向次数 ({max_redirects})")
