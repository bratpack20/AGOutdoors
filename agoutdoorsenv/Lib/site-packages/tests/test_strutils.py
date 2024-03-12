#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *

"""
String operate functions.

"""
import os
import binascii
import unittest
import random
import string
import uuid
from decimal import Decimal

from zenutils import strutils
from zenutils import base64utils
from zenutils import nameutils

def get_test_assets(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "./assets/{filename}".format(
        filename=filename,
    )))

class TestStrUtils(unittest.TestCase):

    def test01(self):
        text = "1,2.3,4.5"
        values = strutils.split(text, [",", "."])
        assert values == ["1", "2", "3", "4", "5"]

    def test02(self):
        text = "1,  2 .  3 , 4 . 5 "
        values = strutils.split(text, [",", "."], strip=True)
        assert values == ["1", "2", "3", "4", "5"]

    def test03(self):
        assert strutils.str_composed_by("abc", "abc") is True
        assert strutils.str_composed_by("abcd", "abc") is False
        assert strutils.str_composed_by("a", "") is False
        assert strutils.str_composed_by("aaa", "a") is True
        assert strutils.str_composed_by("aaa", "b") is False
        assert strutils.str_composed_by("ab", "abc") is True

    def test04(self):
        assert strutils.is_hex_digits("") is False
        assert strutils.is_hex_digits("0") is True
        assert strutils.is_hex_digits("9") is True
        assert strutils.is_hex_digits("a") is True
        assert strutils.is_hex_digits("f") is True
        assert strutils.is_hex_digits("g") is False
        assert strutils.is_hex_digits("0123456789abcdefABCDEF") is True

    def test05(self):
        assert strutils.join_lines("") == ""
        assert strutils.join_lines("a") == "a"
        assert strutils.join_lines("a\n") == "a"
        assert strutils.join_lines("a\nb") == "ab"
        assert strutils.join_lines("a\nb\n") == "ab"
        assert strutils.join_lines("a") == "a"
        assert strutils.join_lines("a\r") == "a"
        assert strutils.join_lines("a\rb") == "ab"
        assert strutils.join_lines("a\rb\r") == "ab"
        assert strutils.join_lines("a") == "a"
        assert strutils.join_lines("a\r\n") == "a"
        assert strutils.join_lines("a\r\nb") == "ab"
        assert strutils.join_lines("a\r\nb\r\n") == "ab"
        assert strutils.join_lines("a\rb\nc\r\n") == "abc"

    def test06(self):
        assert strutils.is_urlsafeb64_decodable("") is False
        assert strutils.is_urlsafeb64_decodable("a") is False
        assert strutils.is_urlsafeb64_decodable("ab") is False
        assert strutils.is_urlsafeb64_decodable("abc") is False
        assert strutils.is_urlsafeb64_decodable("abcde") is False
        assert strutils.is_urlsafeb64_decodable("abcdef") is False
        assert strutils.is_urlsafeb64_decodable("abcdefg") is False
        assert strutils.is_urlsafeb64_decodable("abcdefgh") is True
        assert strutils.is_urlsafeb64_decodable("abcdefghi") is False
        text = base64utils.urlsafe_b64encode(os.urandom(16)).decode()
        assert strutils.is_urlsafeb64_decodable(text) is True

    def test07(self):
        assert strutils.is_base64_decodable("") is False
        assert strutils.is_base64_decodable(" ") is False
        assert strutils.is_base64_decodable("a") is False
        assert strutils.is_base64_decodable("a    ") is False
        assert strutils.is_base64_decodable("ab") is False
        assert strutils.is_base64_decodable("ab    ") is False
        assert strutils.is_base64_decodable("abc") is False
        assert strutils.is_base64_decodable("abcd") is True
        assert strutils.is_base64_decodable("abcd  ") is True
        assert strutils.is_base64_decodable("abcde") is False
        assert strutils.is_base64_decodable("abcdef") is False
        assert strutils.is_base64_decodable("abcdefg") is False
        assert strutils.is_base64_decodable("abcdefgh") is True
        assert strutils.is_base64_decodable("abcdefghi") is False
        text = base64utils.encodebytes(os.urandom(4096)).decode()
        result = strutils.is_base64_decodable(text)
        assert result is True

    def test08(self):
        assert strutils.is_unhexlifiable("") is False
        assert strutils.is_unhexlifiable("a") is False
        assert strutils.is_unhexlifiable("ab") is True
        assert strutils.is_unhexlifiable("abc") is False
        assert strutils.is_unhexlifiable("abcd") is True
        assert strutils.is_unhexlifiable("abcde") is False
        assert strutils.is_unhexlifiable("abcdef") is True
        assert strutils.is_unhexlifiable("abcdefg") is False
        assert strutils.is_unhexlifiable("abcdefgh") is False
        assert strutils.is_unhexlifiable("abcdefghi") is False
        assert strutils.is_unhexlifiable("6869") is True
        text = binascii.hexlify(os.urandom(4096)).decode()
        result = strutils.is_unhexlifiable(text)
        assert result is True

    def test09(self):
        assert strutils.split("", ",") == []
        assert strutils.split("a", ",") == ["a"]
        assert strutils.split("a,b", ",") == ["a", "b"]
        assert strutils.split("a,b,", ",") == ["a", "b", ""]

    def test10(self):
        assert strutils.text_display_length("") == 0
        assert strutils.text_display_length("a") == 1
        assert strutils.text_display_length("测") == 2
        assert strutils.text_display_length("测试") == 4
        assert strutils.text_display_length("测试", unicode_display_length=3) == 6
        assert strutils.text_display_length("a测试") == 5
        assert strutils.text_display_length("ab测试") == 6
        assert strutils.text_display_length("ab测试a") == 7
        assert strutils.text_display_length("ab测试ab") == 8

    def test11(self):
        assert strutils.text_display_shorten("", 5) == strutils.force_text("")
        assert strutils.text_display_shorten("a", 5) == strutils.force_text("a")
        assert strutils.text_display_shorten("ab", 5) == strutils.force_text("ab")
        assert strutils.text_display_shorten("abc", 5) == strutils.force_text("abc")
        assert strutils.text_display_shorten("abcd", 5) == strutils.force_text("abcd")
        assert strutils.text_display_shorten("abcde", 5) == strutils.force_text("abcde")
        assert strutils.text_display_shorten("abcdef", 5) == strutils.force_text("ab...")
        assert strutils.text_display_shorten("abcdefg", 5) == strutils.force_text("ab...")
        assert strutils.text_display_shorten("abcdefgh", 5) == strutils.force_text("ab...")
        assert strutils.text_display_shorten("测", 5) == strutils.force_text("测")
        assert strutils.text_display_shorten("测测", 5) == strutils.force_text("测测")
        assert strutils.text_display_shorten("测测测", 5) == strutils.force_text("测...")
        assert strutils.text_display_shorten("测测测测", 5) == strutils.force_text("测...")
        assert strutils.text_display_shorten("测测测测测", 5) == strutils.force_text("测...")
        assert strutils.text_display_shorten("a测", 5) == strutils.force_text("a测")
        assert strutils.text_display_shorten("a测测", 5) == strutils.force_text("a测测")
        assert strutils.text_display_shorten("a测测测", 5) == strutils.force_text("a...")
        assert strutils.text_display_shorten("a测测测测", 5) == strutils.force_text("a...")
        assert strutils.text_display_shorten("a测测测测测", 5) == strutils.force_text("a...")

    def test12(self):
        assert strutils.wholestrip("a b") == "ab"
        assert strutils.wholestrip(" a b ") == "ab"

    def test13(self):
        s1 = os.urandom(random.randint(0, 1024))
        s21 = binascii.hexlify(s1).decode()
        s22 = base64utils.encodebytes(s1).decode()
        s23 = base64utils.urlsafe_b64encode(s1).decode()
        s24 = s1
        s31 = strutils.smart_get_binary_data(s21)
        s32 = strutils.smart_get_binary_data(s22)
        s33 = strutils.smart_get_binary_data(s23)
        s34 = strutils.smart_get_binary_data(s24)
        assert s1 == s31 == s32 == s33 == s34

    def test14(self):
        assert strutils.is_chinese_character("是") is True
        assert strutils.is_chinese_character("1") is False

    def test15(self):
        for length in range(1024):
            a = os.urandom(length)
            b = strutils.binarify(a)
            c = strutils.unbinarify(b)
            assert a == c

    def test16(self):
        assert strutils.ints2bytes([]) == b''
        assert strutils.ints2bytes([ord('a'), ord('b'), ord('c')]) == b'abc'
        assert strutils.ints2bytes([0, 1, 2, 255]) == b'\x00\x01\x02\xff'
        assert strutils.ints2bytes([256, 257, 65534, 65535, 65536]) == b'\x01\x00\x01\x01\xff\xfe\xff\xff\x01\x00\x00'

    def test17(self):
        assert strutils.force_numberic(1) == 1
        assert strutils.force_numberic(1.2) == 1.2
        assert strutils.force_numberic("1") == 1
        assert strutils.force_numberic("1.2") == 1.2

    def test18(self):
        assert strutils.force_float(1) == 1.0
        assert strutils.force_float(1.2) == 1.2
        assert strutils.force_float("1") == 1.0
        assert strutils.force_float("1.2") == 1.2

    def test19(self):
        assert strutils.char_force_to_int(None) is None
        assert strutils.force_bytes(None) is None
        assert strutils.force_text(None) is None
        assert strutils.force_int(None) is None

    def test20(self):
        t1 = "测试"
        assert strutils.force_text(t1.encode("gbk"), ["utf-8", "gb18030"]) == t1

    def test21(self):
        assert len(strutils.substrings("")) == 0
        assert len(strutils.substrings("a")) == 1
        assert len(strutils.substrings("ab")) == 3
        assert len(strutils.substrings("aa")) == 2
        assert len(strutils.substrings("abc")) == len(["a", "b", "c", "ab", "bc", "abc"])
        assert len(strutils.substrings("abc", 2)) == len(["ab", "bc"])
        assert len(strutils.substrings("abc", 3)) == 1
        assert len(strutils.substrings("abc", 1)) == 3
        assert len(strutils.substrings("abc", [1, 2])) == 5
        assert len(strutils.substrings(b"abc", [1, 2])) == 5
        assert len(strutils.substrings(b"abc")) == len([b"a", b"b", b"c", b"ab", b"bc", b"abc"])

    def test22(self):
        assert len(strutils.combinations("a", 2)) == 1 ** 2
        assert len(strutils.combinations("ab", 2)) == 2 ** 2
        assert len(strutils.combinations("abc", 2)) == 3 ** 2
        assert len(strutils.combinations("a", 3)) == 1 ** 3
        assert len(strutils.combinations("ab", 3)) == 2 ** 3
        assert len(strutils.combinations(string.digits, 2)) == 10 ** 2
        assert len(strutils.combinations(string.digits, 3)) == 10 ** 3
        assert len(strutils.combinations(string.ascii_lowercase, 3)) == 26 ** 3
        assert len(strutils.combinations(["a", "cd"], 3)) == 8
        assert len(strutils.combinations(["ab", "cd"], 3)) == 8
        assert len(strutils.combinations([b"ab", b"cd"], 3)) == 8
        assert len(strutils.combinations(["aa", "bb"], 3)) == 6
        assert len(strutils.combinations(["abc"], 1)) == 3
        assert len(strutils.combinations(["abc"], 2)) == 3
        assert len(strutils.combinations(["abc"], 3)) == 3
        assert len(strutils.combinations(["abc"], 4)) == 3
        assert len(strutils.combinations(["abc"], 5)) == 3
        assert len(strutils.combinations(["abc"], 6)) == 3
        assert len(strutils.combinations(["abc"], 7)) == 3
        assert len(strutils.combinations(["abc"], 8)) == 3

    def test23(self):
        assert strutils.captital_number(0) == "零圆"
        assert strutils.captital_number(1) == "壹圆"
        assert strutils.captital_number(10) == "壹拾圆"
        assert strutils.captital_number(12) == "壹拾贰圆"
        assert strutils.captital_number(100) == "壹佰圆"
        assert strutils.captital_number(102) == "壹佰零贰圆"
        assert strutils.captital_number(123) == "壹佰贰拾叁圆"
        assert strutils.captital_number(1000) == "壹仟圆"
        assert strutils.captital_number(1002) == "壹仟零贰圆"
        assert strutils.captital_number(1023) == "壹仟零贰拾叁圆"
        assert strutils.captital_number(1234) == "壹仟贰佰叁拾肆圆"
        assert strutils.captital_number(10000) == "壹万圆"
        assert strutils.captital_number(10002) == "壹万零贰圆"
        assert strutils.captital_number(10023) == "壹万零贰拾叁圆"
        assert strutils.captital_number(10234) == "壹万零贰佰叁拾肆圆"
        assert strutils.captital_number(10204) == "壹万零贰佰零肆圆"
        assert strutils.captital_number(12345) == "壹万贰仟叁佰肆拾伍圆"
        assert strutils.captital_number(12005) == "壹万贰仟零伍圆"
        assert strutils.captital_number(112005) == "壹拾壹万贰仟零伍圆"
        assert strutils.captital_number(10112005) == "壹仟零壹拾壹万贰仟零伍圆"
        assert strutils.captital_number(100000000) == "壹亿圆"
        assert strutils.captital_number(100000002) == "壹亿零贰圆"
        assert strutils.captital_number(100030000) == "壹亿零叁万圆"
        assert strutils.captital_number(100003000) == "壹亿零叁仟圆"
        assert strutils.captital_number(123100003000) == "壹仟贰佰叁拾壹亿零叁仟圆"
        assert strutils.captital_number(1234567890123) == "壹万贰仟叁佰肆拾伍亿陆仟柒佰捌拾玖万零壹佰贰拾叁圆"
        assert strutils.captital_number(1234567) == "壹佰贰拾叁万肆仟伍佰陆拾柒圆"

    def test24(self):
        assert strutils.captital_number(0.1) == "零圆壹角"
        assert strutils.captital_number(0.01) == "零圆壹分"
        assert strutils.captital_number(0.001) == "零圆壹厘"
        assert strutils.captital_number(0.0001) == "零圆壹毫"
        assert strutils.captital_number(0.00001) == "零圆壹丝"
        assert strutils.captital_number(0.000001) == "零圆壹忽"
        assert strutils.captital_number(0.0000001) == "零圆壹微"
        assert strutils.captital_number(0.00000001) == "零圆"
        assert strutils.captital_number(0.12) == "零圆壹角贰分"
        assert strutils.captital_number(0.123) == "零圆壹角贰分叁厘"
        assert strutils.captital_number(0.1234) == "零圆壹角贰分叁厘肆毫"
        assert strutils.captital_number(0.12345) == "零圆壹角贰分叁厘肆毫伍丝"
        assert strutils.captital_number(0.123456) == "零圆壹角贰分叁厘肆毫伍丝陆忽"
        assert strutils.captital_number(0.1234567) == "零圆壹角贰分叁厘肆毫伍丝陆忽柒微"
        assert strutils.captital_number(0.12345678) == "零圆壹角贰分叁厘肆毫伍丝陆忽柒微"

    def test25(self):
        assert strutils.camel("hello") == "Hello"
        assert strutils.camel("hello world") == "Hello World"
        assert strutils.camel(" hello ") == " Hello "
        assert strutils.camel("hello  world") == "Hello  World"
        assert strutils.camel("hello-world") == "Hello-World"
        assert strutils.camel("hello_world") == "Hello_World"

        assert strutils.camel("hello", clean=True) == "Hello"
        assert strutils.camel("hello world", clean=True) == "HelloWorld"
        assert strutils.camel(" hello ", clean=True) == "Hello"
        assert strutils.camel("hello  world", clean=True) == "HelloWorld"
        assert strutils.camel("hello-world", clean=True) == "HelloWorld"
        assert strutils.camel("hello_world", clean=True) == "HelloWorld"

    def test26(self):
        assert strutils.format_with_mapping("{}{}", strutils.none_to_empty_string, 1, None) == "1"
        assert strutils.format_with_mapping("{a}{b}", strutils.none_to_empty_string, a=1, b=None) == "1"
        assert strutils.format_with_mapping("{}{a}{}{b}", strutils.none_to_empty_string, 1, None, a=3, b=None) == "13"
        assert strutils.format_with_mapping("{:d}:{:}", strutils.no_mapping, 1, None) == "1:None"

    def test27(self):
        assert strutils.unquote('''"hello"''') == "hello"
        assert strutils.unquote('"""hello"""') == "hello"
        assert strutils.unquote('“hello”') == "hello"
        assert strutils.unquote('‘hello’') == "hello"

    def test28(self):
        assert strutils.is_uuid(uuid.uuid4())
        assert strutils.is_uuid(uuid.uuid4().bytes)
        assert strutils.is_uuid("abc") == False
        assert strutils.is_uuid("abcdefghijklmnopqrstuvwxyz") == False
        assert strutils.is_uuid("{12345678-1234-5678-1234-567812345678}")
        assert strutils.is_uuid("12345678123456781234567812345678")
        assert strutils.is_uuid("12345678-1234-5678-1234-567812345678")
        assert strutils.is_uuid(strutils.force_text(uuid.uuid4().hex))
        assert strutils.is_uuid(uuid.uuid4().hex)

    def test29(self):
        assert strutils.camel("hello world", clean=True, lower_first=True) == "helloWorld"

    def test30(self):
        assert strutils.stringlist_append("a b c", "a", separator=" ") == "a b c a"
        assert strutils.stringlist_append("a,b,c", "a") == "a,b,c,a"
        assert strutils.stringlist_append("a,b,c", "a", allow_duplicate=False) == "a,b,c"

    def test31(self):
        assert strutils.is_urlsafeb64_decodable("abcd") is True

    def test32(self):
        assert strutils.html_element_css_append("a b c", "a") == "a b c"
        assert strutils.html_element_css_append("a b c", "d") == "a b c d"

    def test33(self):
        assert strutils.remove_prefix("helloworld", "hello") == "world"
        assert strutils.remove_prefix("helloworld", "hi") == "helloworld"
        assert strutils.remove_prefix("helloworld", "") == "helloworld"

    def test34(self):
        assert strutils.remove_suffix("helloworld", "world") == "hello"
        assert strutils.remove_suffix("helloworld", "word") == "helloworld"
        assert strutils.remove_suffix("helloworld", "") == "helloworld"

    def test35(self):
        assert strutils.split2("hello world") == ["hello", "world"]
        assert strutils.split2("hello world !") == ["hello", "world !"]
        assert strutils.split2("1,2,3", ",") == ["1", "2,3"]

    def test36(self):
        assert strutils.is_uuid("90a0332d-7f06-gace-a1e2-3c27e634c17f") == False
        assert strutils.is_uuid("90a0332d-7f06-gace-a1e2-3c27e634c17f", allow_bad_characters=True) == True
        assert strutils.is_uuid("90a0332d-7f06-gace-a1e2-3c27e634c17f-x", allow_bad_characters=True) == False
        assert strutils.is_uuid("123412341234123412341234", allow_bad_characters=True) == False

    def test37(self):
        assert strutils.chunk("", 2) == []
        assert strutils.chunk("1", 2) == ["1"]
        assert strutils.chunk("12", 2) == ["12"]
        assert strutils.chunk("123", 2) == ["12", "3"]
        assert strutils.chunk("1234", 2) == ["12", "34"]
        assert strutils.chunk("", 1) == []
        assert strutils.chunk("1", 1) == ["1"]
        assert strutils.chunk("12", 1) == ["1", "2"]
        assert strutils.chunk("123", 1) == ["1", "2", "3"]

    def test38(self):
        assert strutils.get_all_substrings("a") == set(["a"])
        assert strutils.get_all_substrings("ab") == set(["a", "b", "ab"])
        assert strutils.get_all_substrings("abc") == set(["a", "b", "c", "ab", "bc", "abc"])
        assert strutils.get_all_substrings("abcd") == set(["a", "b", "c", "d", "ab", "bc", "cd", "abc", "bcd", "abcd"])

        assert strutils.get_all_substrings("aa") == set(["a", "aa"])
        assert strutils.get_all_substrings("aab") == set(["a", "b", "aa", "ab", "aab"])
        assert strutils.get_all_substrings("aba") == set(["a", "b", "ab", "ba", "aba"])
        assert strutils.get_all_substrings("abab") == set(["a", "b", "ab", "ba", "aba", "bab", "abab"])

    def test39(self):
        assert strutils.get_all_substrings(b"a") == set([b"a"])
        assert strutils.get_all_substrings(b"ab") == set([b"a", b"b", b"ab"])
        assert strutils.get_all_substrings(b"abc") == set([b"a", b"b", b"c", b"ab", b"bc", b"abc"])
        assert strutils.get_all_substrings(b"abcd") == set([b"a", b"b", b"c", b"d", b"ab", b"bc", b"cd", b"abc", b"bcd", b"abcd"])

        assert strutils.get_all_substrings(b"aa") == set([b"a", b"aa"])
        assert strutils.get_all_substrings(b"aab") == set([b"a", b"b", b"aa", b"ab", b"aab"])
        assert strutils.get_all_substrings(b"aba") == set([b"a", b"b", b"ab", b"ba", b"aba"])
        assert strutils.get_all_substrings(b"abab") == set([b"a", b"b", b"ab", b"ba", b"aba", b"bab", b"abab"])

    def test40(self):
        assert strutils.force_type_to("src", "dst") == "src"
        assert strutils.force_type_to("src", b"dst") == b"src"
        assert strutils.force_type_to(b"src", "dst") == "src"
        assert strutils.force_type_to(b"src", b"dst") == b"src"

    def test41(self):
        assert strutils.simplesplit("a b c") == ["a", "b", "c"]
        assert strutils.simplesplit("a,b,c", ",") == ["a", "b", "c"]
        assert strutils.simplesplit("a,b,c", sep=",") == ["a", "b", "c"]
        assert strutils.simplesplit("a b c", maxsplit=1) == ["a", "b c"]
        assert strutils.simplesplit("a,b,c", ",", 1) == ["a", "b,c"]
        assert strutils.simplesplit("a,b,c", ",", maxsplit=1) == ["a", "b,c"]
        assert strutils.simplesplit("a,b,c", sep=",", maxsplit=1) == ["a", "b,c"]

    def test42(self):
        assert strutils.random_string(8)

        choices = strutils.force_text(string.ascii_letters)
        assert strutils.random_string(8, choices=choices)

        choices = strutils.force_bytes(string.ascii_letters)
        assert strutils.random_string(8, choices=choices)

    def test43(self):
        assert strutils.force_float(None) is None
        assert strutils.force_float(lambda:1.101) == 1.101
        assert strutils.force_float(1.101) == 1.101
        assert strutils.force_float("1.101") == 1.101
        assert strutils.force_float(b"1.101") == 1.101
        assert strutils.force_float(Decimal(1.101)) == 1.101

    def test44(self):
        assert strutils.clean("abc", "ab") == "ab"
        assert strutils.clean(b"abc", b"ab") == b"ab"

    def test45(self):
        assert strutils.strip_string(" hello ") == "hello"
        assert strutils.strip_string(b" hello ") == b"hello"

    def test46(self):
        assert strutils.none_to_empty_string(None) == ""
        assert strutils.none_to_empty_string(False) == False
        assert strutils.none_to_empty_string(True) == True
        assert strutils.none_to_empty_string([]) == []
        assert strutils.none_to_empty_string([1]) == [1]

    def test47(self):
        assert strutils.force_int(None) is None
        assert strutils.force_int(0) == 0
        assert strutils.force_int("1234") == 1234
        assert strutils.force_int(b"1234") == 1234
        assert strutils.force_int("0") == 0
        assert strutils.force_int(b"0") == 0
        assert strutils.force_int("1.23") == 1
        assert strutils.force_int(b"1.23") == 1
        assert strutils.force_int("1.93") == 1
        assert strutils.force_int(b"1.93") == 1
        assert strutils.force_int(1.1) == 1
        assert strutils.force_int(1.9) == 1
        assert strutils.force_int(Decimal(1.101)) == 1
        assert strutils.force_int(Decimal(1.901)) == 1

    def test48(self):
        assert strutils.reverse("hello") == "olleh"
        assert strutils.reverse(b"hello") == b"olleh"
        assert strutils.reverse("") == ""
        assert strutils.reverse(b"") == b""

    def test49(self):
        assert strutils.force_type_to("", "") == ""
        assert strutils.force_type_to("", b"") == b""

    def test50(self):
        data = os.urandom(1024)
        assert strutils.smart_get_binary_data(data) == data
        assert strutils.smart_get_binary_data("hello") == b"hello"

    def test51(self):
        for _ in range(1024):
            name = nameutils.get_random_name()
            for c in name:
                assert strutils.is_chinese_character(c)

    def test52(self):
        assert strutils.unquote("hello") == "hello"

    def test53(self):
        data = uuid.uuid4()
        assert strutils.is_uuid(data)
        assert strutils.is_uuid(data.fields)
        assert strutils.is_uuid(data.bytes)
        assert strutils.is_uuid(str(data))
        assert strutils.is_uuid(data.hex)
    
    def test54(self):
        assert strutils.encodable("hello")
        assert strutils.encodable("测试")
        assert strutils.encodable("测试", encoding="big5") is False

    def test55(self):
        assert strutils.reverse(None) is None

    def test56(self):
        for i in range(1024):
            length = random.randint(0, 128)
            data1 = os.urandom(length)
            data2 = strutils.bytes2ints(data1)
            data3 = strutils.ints2bytes(data2)
            assert data1 == data3

    def test57(self):
        assert strutils.combinations("abc", 5) == strutils.combinations2("abc", 5)
        assert strutils.combinations("abc", 4) == strutils.combinations2("abc", 4)
        assert strutils.combinations("abc", 3) == strutils.combinations2("abc", 3)
        assert strutils.combinations("abc", 2) == strutils.combinations2("abc", 2)
        assert strutils.combinations("abc", 1) == strutils.combinations2("abc", 1)

    def test58(self):
        filename1 = get_test_assets("p1.jpeg")
        format1 = "jpeg"
        data1 = strutils.get_base64image(filename1, format=format1)
        format2, data2 = strutils.parse_base64image(data1)
        assert format1 == format2
        assert data2 == strutils.get_image_bytes(filename1, format=format1)
 
    def test59(self):
        filename1 = get_test_assets("p1.jpeg")
        format1 = "jpeg"
        content = b""
        with open(filename1, "rb") as fobj:
            content = fobj.read()
        data1 = strutils.get_base64image(content, format=format1)
        format2, data2 = strutils.parse_base64image(data1)
        assert format1 == format2
        assert data2 == strutils.get_image_bytes(filename1, format=format1)

    def test60(self):
        from PIL import Image
        image = Image.new("RGB", (1, 1))
        format1 = "webp"
        content = strutils.get_image_bytes(image, format1)
        data1 = strutils.get_base64image(content, format=format1)
        format2, data2 = strutils.parse_base64image(data1)
        assert format1 == format2
        assert data2 == strutils.get_image_bytes(image, format=format1)

    def test61(self):
        from PIL import Image
        image = Image.new("RGB", (1, 1))
        format1 = "webp"
        content1 = strutils.get_image_bytes(image, format1)
        content2 = strutils.get_image_bytes(content1, format1)
        data1 = strutils.get_base64image(content2, format=format1)
        format2, data2 = strutils.parse_base64image(data1)
        assert format1 == format2
        assert data2 == strutils.get_image_bytes(image, format=format1)
