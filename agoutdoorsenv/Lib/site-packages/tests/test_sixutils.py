#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *

import os
import unittest
from zenutils import sixutils
from zenutils import strutils


class TestSixUtils(unittest.TestCase):

    def test01(self):
        assert sixutils.bytes_to_array(b"hello") == [b"h", b"e", b"l", b"l", b"o"]
    
    def test02(self):
        assert sixutils.bstr_to_array(b"hello") == [b"h", b"e", b"l", b"l", b"o"]
        assert sixutils.bstr_to_array("hello") == ["h", "e", "l", "l", "o"]
        data = sixutils.bstr_to_array(os.urandom(16))
        for c in data:
            assert isinstance(c, sixutils.BYTES_TYPE)
        data = sixutils.bstr_to_array(strutils.random_string(16))
        for c in data:
            assert isinstance(c, sixutils.STR_TYPE)

    def test03(self):
        assert sixutils.bchar(0) == b"\x00"
        assert sixutils.bchar(1) == b"\x01"
        assert sixutils.bchar(2) == b"\x02"
        assert sixutils.bchar(3) == b"\x03"
        assert sixutils.bchar(4) == b"\x04"
        assert sixutils.bchar(5) == b"\x05"
        assert sixutils.bchar(6) == b"\x06"
        assert sixutils.bchar(7) == b"\x07"
        assert sixutils.bchar(8) == b"\x08"
        assert sixutils.bchar(9) == b"\x09"
        assert sixutils.bchar(10) == b"\x0a"
        assert sixutils.bchar(11) == b"\x0b"
        assert sixutils.bchar(12) == b"\x0c"
        assert sixutils.bchar(254) == b"\xfe"
        assert sixutils.bchar(255) == b"\xff"

    def test04(self):
        assert sixutils.force_bytes("hello") == b"hello"
        assert sixutils.force_bytes(b"hello") == b"hello"
        assert sixutils.force_text("hello") == "hello"
        assert sixutils.force_text(b"hello") == "hello"
    
    def test05(self):
        assert sixutils.force_bytes(None) is None
        assert sixutils.force_text(None) is None
    
    def test06(self):
        assert sixutils.force_bytes(lambda:"hello") == b"hello"
        assert sixutils.force_bytes(lambda:b"hello") == b"hello"
        assert sixutils.force_text(lambda:"hello") == "hello"
        assert sixutils.force_text(lambda:b"hello") == "hello"

        assert sixutils.BYTES(lambda:"hello") == b"hello"
        assert sixutils.BYTES(lambda:b"hello") == b"hello"
        assert sixutils.TEXT(lambda:"hello") == "hello"
        assert sixutils.TEXT(lambda:b"hello") == "hello"

    def test07(self):
        class Hello(object):
            def __init__(self, name):
                self.name = name
            
            def __repr__(self):
                return "hi, {name}.".format(name=self.name)

        assert sixutils.force_bytes(lambda:Hello("tom")) == b"hi, tom."
        assert sixutils.force_text(lambda:Hello("tom")) == "hi, tom."
        assert sixutils.force_bytes(Hello("tom")) == b"hi, tom."
        assert sixutils.force_text(Hello("tom")) == "hi, tom."
    
    def test08(self):
        with self.assertRaises(UnicodeDecodeError):
            sixutils.TEXT(os.urandom(1024))

    def test09(self):
        assert sixutils.force_bytes(b'hello') == b'hello'
        assert sixutils.force_bytes('测试') == '测试'.encode('utf-8')
        assert sixutils.force_bytes('hello') == b'hello'
        assert sixutils.force_bytes(1234) == b'1234'
        assert sixutils.force_bytes([1,2,3]) == b"[1, 2, 3]"
    
    def test10(self):
        assert sixutils.force_text(b'hello') == 'hello'
        assert sixutils.force_text('测试'.encode('utf-8')) == '测试'
        assert sixutils.force_text('hello') == 'hello'
        assert sixutils.force_text(1234) == '1234'
        assert sixutils.force_text([1,2,3]) == "[1, 2, 3]"

    def test11(self):
        data = {"测试": "测试"}
        if sixutils.PY2:
            assert sixutils.force_text(data) == """{u'\\u6d4b\\u8bd5': u'\\u6d4b\\u8bd5'}"""
        else:
            assert sixutils.force_text(data) == """{'测试': '测试'}"""

    def test12(self):
        data = {"测试": "测试"}
        if sixutils.PY2:
            assert sixutils.force_bytes(data) == b"{u'\\u6d4b\\u8bd5': u'\\u6d4b\\u8bd5'}"
        else:
            assert sixutils.force_bytes(data) == b"{'\xe6\xb5\x8b\xe8\xaf\x95': '\xe6\xb5\x8b\xe8\xaf\x95'}"
