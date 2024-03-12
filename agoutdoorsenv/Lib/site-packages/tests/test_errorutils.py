#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *

import os
import sys
import json
import unittest

from zenutils import errorutils

class TestBizError(unittest.TestCase):

    def test01(self):
        e = errorutils.BizError()
        assert e.code
        assert e.message
        assert e.json

    def test02(self):
        with self.assertRaises(errorutils.BizError):
            raise errorutils.BizError()

    def test03(self):
        e = errorutils.BizError()
        if PY2:
            es = unicode(e)
        else:
            es = str(e)
        esd = json.loads(es)
        assert esd["code"]
        assert esd["message"]

    def test04(self):
        e = errorutils.BizError()
        es = repr(e)
        esd = json.loads(es)
        assert esd["code"]
        assert esd["message"]

    def test05(self):
        e1 = errorutils.BizError("error007")
        e2 = errorutils.BizError(e1)
        assert e1.code == e2.code
        assert e1.message == e2.message

    def test06(self):
        e1 = errorutils.BizError("missing field: {fields}...", fields="appid, appkey")
        assert e1.message == "missing field: appid, appkey..."

    def test07(self):
        e1 = errorutils.BizError(fields="appid, appkey")
        assert not "appid, appkey" in e1.message

    def test08(self):
        assert errorutils.OK().message == "正常。"

    def test09(self):
        error = errorutils.BizError(RuntimeError("hi"))
        assert error.message == "hi"

    def test10(self):
        error = errorutils.BizError(RuntimeError({
            "a": "a",
            "b": [1,2,3],
            "c": b"hello",
            "d": os.urandom(1024),
        }))
        print(error)
        assert "hello" in error.message

    def test11(self):
        error = errorutils.BizError({
            "code": 1234,
            "message": "hello world"
        })
        assert error.code == 1234
        assert error.message == "hello world"

    def test12(self):
        lang = errorutils.get_language()

        errorutils.OK().message == "正常。"

        errorutils.set_language("en")
        errorutils.OK().message == "OK"

        errorutils.set_language(lang)

    def test13(self):
        error = errorutils.BizError(ValueError("hello"))
        assert error.code == 226
        assert error.message == "hello"
    
    def test14(self):
        error = errorutils.BizError(ValueError(508, "hello"))
        assert error.code == 508
        assert error.message == "hello"

    def test15(self):
        error = errorutils.BizError(ValueError(508, "hello", "world"))
        assert error.code == 508
        assert error.message == """hello world"""

    def test18(self):
        e1 = RuntimeError('hello', 'world')
        e2 = errorutils.BizError(e1)
        assert e2.message == "hello world"

    def test19(self):
        e1 = RuntimeError('hello world')
        e2 = errorutils.BizError(e1)
        assert e2.message == "hello world"

    def test20(self):
        error_message = "错误原因"
        e1 = RuntimeError(error_message.encode("utf-8"))
        e2 = errorutils.BizError(e1)
        assert e2.message == error_message

    def test21(self):
        error_message1 = "错误原因："
        error_message2 = "空间不足。"
        e1 = RuntimeError(error_message1, error_message2.encode("gb18030"))
        e2 = errorutils.BizError(e1)
        assert e2.message == error_message1 + " " + error_message2

    def test22(self):
        error_reason = "空间不足"
        error_message = "错误原因：{reason}..."
        e2 = errorutils.BizError(error_message, reason=error_reason)
        assert e2.message == error_message.format(reason=error_reason)

    def test23(self):
        error_reason = "空间不足"
        error_message = "错误原因：{reason}..."
        e2 = errorutils.BizError(error_message.encode("utf-8"), reason=error_reason)
        assert e2.message == error_message.format(reason=error_reason)

    def test24(self):
        a = errorutils.BizError()
        b = repr(a)
        c = str(a)
        print(b)
        print(c)
        assert b
        assert c
        if PY2:
            d = unicode(a)
            assert d

    def test25(self):
        # 具体的异常不能是能用异常
        error = errorutils.BizError(ZeroDivisionError())
        assert error.code!= 1
        assert not error.message in ["Error", "异常！"]

