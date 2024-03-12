#!/usr/bin/env python
# -*- coding: utf8 -*-
"""XMLRPC服务相关工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
from zenutils.sixutils import *

__all__ = [
    "SimpleAuthMixin",
    "SimpleAuthTransport",
    "SimpleAuthSafeTransport",
]

import uuid
import time
import binascii
from xmlrpc.client import Transport
from xmlrpc.client import SafeTransport

from zenutils import hashutils


class SimpleAuthTransport(Transport):
    """为xmlrpc客户端添加SimpleToken认证请求头。"""

    def __init__(
        self,
        use_datetime=False,
        use_builtin_types=False,
        *,
        headers=(),
        auth_header_name="App-Auth",
        auth_content_template="{appid}{reqts}{reqid}{appkey}",
        auth_method="sm3",
        auth_appid=None,
        auth_appkey=None
    ):
        """
        @param use_datetime bool
        @param use_builtin_types bool
        @headers *
        @param headers
        @param auth_header_name SimpleToken认证请求头名称
        @param auth_content_template SimpleToken认证签名模板
        @param auth_method SimpleToken认证签名算法
        @param auth_appid SimpleToken认证APPID
        @param auth_appkey SimpleToken认证APPKEY
        """
        super().__init__(use_datetime, use_builtin_types, headers=headers)
        self.auth_header_name = auth_header_name
        self.auth_content_template = auth_content_template
        self.auth_method = auth_method
        self.auth_appid = auth_appid
        self.auth_appkey = auth_appkey

    def send_headers(self, connection, headers):
        """重载Transport的send_headers方法。在发送headers前，自动加入SimpleToken认证所需要的请求头。"""
        # 随机请求流水号: reqid
        reqid = str(uuid.uuid4()) + "-" + str(uuid.uuid4())
        # 当前请求时间戳: reqts
        reqts = str(int(time.time() * 1000))
        # 请求认证签名内容
        content = self.auth_content_template.format(
            appid=self.auth_appid, appkey=self.auth_appkey, reqts=reqts, reqid=reqid
        )
        # 请求认证签名
        sign = hashutils.get_hash_hexdigest(content, method=self.auth_method)
        # 请求认证头
        app_auth = binascii.hexlify(
            "::".join([self.auth_appid, reqts, reqid, sign]).encode("utf-8 ")
        ).decode("utf-8")
        # 更新请求头
        updated_flag = False
        for item in headers:
            if item[0] == self.auth_header_name:
                item[1] = app_auth
                updated_flag = True
                break
        if not updated_flag:
            headers.append([self.auth_header_name, app_auth])
        # 发送请求头
        return super().send_headers(connection, headers)


class SimpleAuthSafeTransport(SafeTransport, SimpleAuthTransport):
    """为xmlrpc客户端添加SimpleToken认证请求头。参数详见 @see SimpleAuthTransport。"""

    pass
