#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *


import unittest
import os
import binascii
import uuid
from zenutils import typingutils
from zenutils import base64utils

class TestTypingUtils(unittest.TestCase):

    def test01(self):
        assert typingutils.smart_cast(int, "12") == 12
        assert typingutils.smart_cast(float, "12.34") == 12.34
        assert typingutils.smart_cast(bool, "true") == True
        assert typingutils.smart_cast(list, "1,2,3") == ["1", "2", "3"]
        assert typingutils.smart_cast(dict, """{"a": "a", "b": "b"}""") == {"a": "a", "b": "b"}
        assert typingutils.smart_cast(STR_TYPE, b"hello") == "hello"
        assert isinstance("6869", STR_TYPE)
        result = typingutils.smart_cast(BYTES_TYPE, "6869")
        assert isinstance(result, BYTES_TYPE)
        assert result == b"hi"

    def test02(self):
        assert typingutils.smart_cast(bool, "True") is True
        assert typingutils.smart_cast(bool, "False") is False
        assert typingutils.smart_cast(bool, "1") is True
        assert typingutils.smart_cast(bool, "0") is False
        assert typingutils.smart_cast(bool, "y") is True
        assert typingutils.smart_cast(bool, "n") is False
        assert typingutils.smart_cast(bool, "yes") is True
        assert typingutils.smart_cast(bool, "no") is False
        assert typingutils.smart_cast(bool, 1) is True
        assert typingutils.smart_cast(bool, 0) is False
        assert typingutils.smart_cast(bool, True) is True
        assert typingutils.smart_cast(bool, False) is False
        assert typingutils.smart_cast(bool, 1.1) is True
        assert typingutils.smart_cast(bool, 0.0) is False

    def test03(self):
        assert typingutils.smart_cast(int, 1) == 1
        assert typingutils.smart_cast(int, 0) == 0
        assert typingutils.smart_cast(int, "1") == 1
        assert typingutils.smart_cast(int, "0") == 0

    def test04(self):
        assert typingutils.smart_cast(STR_TYPE, "a") == "a"
        assert typingutils.smart_cast(STR_TYPE, "测试") == "测试"
        assert typingutils.smart_cast(STR_TYPE, 1) == "1"
        assert typingutils.smart_cast(STR_TYPE, True) == "True"
        assert typingutils.smart_cast(STR_TYPE, False) == "False"
        assert typingutils.smart_cast(STR_TYPE, "测试".encode("utf-8")) == "测试"
        assert typingutils.smart_cast(STR_TYPE, "测试".encode("gbk")) == "测试"

    def test05(self):
        assert typingutils.smart_cast(BYTES_TYPE, "a") == b"a"
        assert typingutils.smart_cast(BYTES_TYPE, b"a") == b"a"
        assert typingutils.smart_cast(BYTES_TYPE, "YQ==") == b"a"
        assert typingutils.smart_cast(BYTES_TYPE, "YWI=") == b"ab"
        assert typingutils.smart_cast(BYTES_TYPE, "6162") == b"ab"
        assert isinstance("测试", STR_TYPE)
        assert typingutils.smart_cast(BYTES_TYPE, "测试") == "测试".encode("utf-8")

    def test06(self):
        s = os.urandom(16)
        t1 = binascii.hexlify(s).decode()
        t2 = base64utils.encodebytes(s).decode()
        t3 = base64utils.urlsafe_b64encode(s).decode()
        assert typingutils.smart_cast(BYTES_TYPE, t1) == s
        assert typingutils.smart_cast(BYTES_TYPE, t2) == s
        assert typingutils.smart_cast(BYTES_TYPE, t3) == s

    def test07(self):
        assert typingutils.smart_cast(dict, {"a": "a"})["a"] == "a"
        assert typingutils.smart_cast(dict, """{"a": "a"}""")["a"] == "a"
        assert typingutils.smart_cast(dict, [("a", "a")])["a"] == "a"

    def test08(self):
        assert typingutils.smart_cast(list, [1, 2, 3])[0] == 1
        assert typingutils.smart_cast(list, """[1, 2, 3]""")[0] == 1
        assert typingutils.smart_cast(list, """1 , 2 , 3""")[0] == "1"

    def test09(self):
        assert typingutils.smart_cast(typingutils.Number, 1) == 1
        assert typingutils.smart_cast(typingutils.Number, 1.0) == 1.0
        assert typingutils.smart_cast(typingutils.Number, "1") == 1
        assert typingutils.smart_cast(typingutils.Number, "1.0") == 1.0

    def test10(self):
        assert typingutils.smart_cast(int, "") == None
        assert typingutils.smart_cast(float, "") == None
        assert typingutils.smart_cast(list, "") == None
        assert typingutils.smart_cast(dict, "") == None

    def test11(self):
        data1 = uuid.uuid4()
        assert typingutils.smart_cast(uuid.UUID, data1) == data1
        assert typingutils.smart_cast(uuid.UUID, data1.hex) == data1
        assert typingutils.smart_cast(uuid.UUID, data1.bytes) == data1
        assert typingutils.smart_cast(uuid.UUID, data1.fields) == data1

    def test12(self):
        # test only if typing is available
        try:
            import typing
        except:
            typing = None
        if typing:
            assert typingutils.smart_cast(typing.List, "[1, 2, 3]") == [1, 2, 3]
            assert typingutils.smart_cast(typing.Mapping, """{"a": "a", "b": "b"}""") == {"a": "a", "b": "b"}
