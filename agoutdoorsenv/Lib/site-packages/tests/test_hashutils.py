#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
from sys import prefix
from zenutils.sixutils import *

import os
import uuid
import random
import unittest

from zenutils import hashutils
from zenutils import strutils


class TestHashUtils(unittest.TestCase):
    def test01(self):
        text = hashutils.get_md5()
        assert text == "d41d8cd98f00b204e9800998ecf8427e"

    def test02(self):
        text = hashutils.get_md5(b"a")
        assert text == "0cc175b9c0f1b6a831c399e269772661"

    def test03(self):
        text = hashutils.get_md5("a", b"b")
        assert text == "187ef4436122d1cc2f40dc2b92f0eba0"

    def test04(self):
        text = hashutils.get_md5("a", "b", 1)
        assert text == "68b6a776378decbb4a79cda89087c4ce"

    def test05(self):
        text = hashutils.get_sha1("a", 1, True)
        assert text == "3251aeb0f68984b60d7cb2ed7f2505bee819a7c7"

    def test06(self):
        text = hashutils.get_sha1_base64("a", 1, True, 0.01)
        assert text == "yrZxIUBkyZ03qTIMbYORcBdnFRc="

    def test07(self):
        text = hashutils.get_pbkdf2_hmac(
            "testpassword", salt="bPBMORgAZP53", iterations=150000, hash_name="sha256"
        )
        assert (
            text
            == "pbkdf2_sha256$150000$bPBMORgAZP53$yPCstMcQYC9Rgn0h2mT0egPjUdW5T7WUiViib9Sn0dM="
        )

    def test08(self):
        text = hashutils.get_pbkdf2_sha256(
            "testpassword", salt="bPBMORgAZP53", iterations=150000
        )
        assert (
            text
            == "pbkdf2_sha256$150000$bPBMORgAZP53$yPCstMcQYC9Rgn0h2mT0egPjUdW5T7WUiViib9Sn0dM="
        )

    def test09(self):
        text = hashutils.get_pbkdf2_sha256("just a test")
        assert hashutils.validate_pbkdf2_sha256("just a test", text)

    def test10(self):
        text = hashutils.get_pbkdf2_md5("just a test")
        assert hashutils.validate_pbkdf2_md5("just a test", text)

        text = hashutils.get_pbkdf2_md5(b"just a test")
        assert hashutils.validate_pbkdf2_md5(b"just a test", text)

        text = hashutils.get_pbkdf2_md5(b"just a test")
        assert hashutils.validate_pbkdf2_md5("just a test", text)

        text = hashutils.get_pbkdf2_md5("just a test")
        assert hashutils.validate_pbkdf2_md5(b"just a test", text)

    def test11(self):
        assert "5vNnRsy6QsKIrPkG5ja7J46ut+g=" == hashutils.get_sha1_base64(
            b"just a test"
        )
        assert "5vNnRsy6QsKIrPkG5ja7J46ut+g=" == hashutils.get_sha1_base64(
            "just a test"
        )

    def test12(self):
        filename = "{0}.txt".format(str(uuid.uuid4()))
        try:
            length = random.randint(0, 1024 * 1024 * 16)
            stream = os.urandom(length)
            with open(filename, "wb") as fobj:
                fobj.write(stream)
            code1 = hashutils.get_file_md5(filename)
            code2 = hashutils.get_md5(stream)
            assert code1 == code2

            code3 = hashutils.get_file_sha(filename)
            code4 = hashutils.get_sha1(stream)
            assert code3 == code4
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test13(self):
        assert hashutils.is_the_same_hash_method(
            hashutils.method_load("md5"), hashutils.method_load(b"md5")
        )
        assert hashutils.is_the_same_hash_method(
            hashutils.method_load("sha1"), hashutils.method_load(b"sha1")
        )
        assert hashutils.is_the_same_hash_method(
            hashutils.method_load("sha256"), hashutils.method_load(b"sha256")
        )

    def test14(self):
        methods = [
            "MD5",
            "SHA",
            "SHA1",
            "SHA224",
            "SHA256",
            "SHA384",
            "SHA512",
        ]
        for method in methods:
            data1 = strutils.random_string(12)
            data2 = hashutils.get_password_hash(data1, method=method)
            result = hashutils.validate_password_hash(data2, data1)
            assert result

    def test15(self):
        methods = [
            "SMD5",
            "SSHA",
            "SSHA1",
            "SSHA224",
            "SSHA256",
            "SSHA384",
            "SSHA512",
        ]
        for method in methods:
            data1 = strutils.random_string(12)
            data2 = hashutils.get_password_hash(data1, method=method)
            result = hashutils.validate_password_hash(data2, data1)
            assert result

    def test16(self):
        for method in hashutils.get_password_hash_methods():
            if not method.startswith("SH"):
                continue
            data1 = strutils.random_string(12)
            data2 = hashutils.get_password_hash(data1, method=method)
            result = hashutils.validate_password_hash(data2, data1)
            print(method, data1, data2, result)
            assert result

    def test17(self):
        """
        检查哈希结果前缀是否存在冲突。
        """
        prefixes = []
        for _, method in hashutils.PASSWORD_HASH_METHODS.items():
            if not hasattr(method, "prefix"):
                continue

            assert not method.prefix in prefixes

            for p1 in prefixes:
                assert not p1.startswith(method.prefix)
                assert not method.prefix.startswith(p1)

            prefixes.append(prefix)

    def test18(self):
        data1 = strutils.random_string(8)
        data2 = hashutils.get_password_hash(data1, "sm3")
        assert data2

    def test19(self):
        for method in hashutils.get_password_hash_methods():
            print(method)
            data1 = strutils.random_string(8)
            data2 = hashutils.get_password_hash(data1, method)
            print(method, data1, data2)
            result = hashutils.validate_password_hash(data2, data1)
            print(method, data1, data2, result)
            assert data1
            assert data2
            assert result

    def test20(self):
        r1 = hashutils.get_hash_digest("hello world", method="md5")
        r2 = hashutils.get_hash_digest("hello world", method="sha")
        r3 = hashutils.get_hash_digest("hello world", method="sha256")
        assert r1 == b'^\xb6;\xbb\xe0\x1e\xee\xd0\x93\xcb"\xbb\x8fZ\xcd\xc3'
        assert r2 == b"*\xael5\xc9O\xcf\xb4\x15\xdb\xe9_@\x8b\x9c\xe9\x1e\xe8F\xed"
        assert (
            r3
            == b"\xb9M'\xb9\x93M>\x08\xa5.R\xd7\xda}\xab\xfa\xc4\x84\xef\xe3zS\x80\xee\x90\x88\xf7\xac\xe2\xef\xcd\xe9"
        )
