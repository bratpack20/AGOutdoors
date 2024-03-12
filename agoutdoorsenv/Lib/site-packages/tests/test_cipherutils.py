#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *


import unittest
import random
import string
import os

from zenutils import randomutils
from zenutils import cipherutils
from zenutils import listutils

class TestCipherUtils(unittest.TestCase):
   
    def test01(self):
        password = "".join(randomutils.choices(string.ascii_letters, k=random.randint(4, 16)))
        cipher = cipherutils.S12Cipher(password=password)
        text1 = ("".join(randomutils.choices(string.ascii_letters, k=random.randint(0, 1024)))).encode()
        data = cipher.encrypt(text1)
        text2 = cipher.decrypt(data)
        assert text1 == text2
    
    def test02(self):
        password = "".join(randomutils.choices(string.ascii_letters, k=random.randint(4, 16)))
        cipher = cipherutils.S12Cipher(password=password)
        text1 = "hello"
        text2 = "hello world"
        data1 = cipher.encrypt(text1)
        data2 = cipher.encrypt(text2)
        assert data2.startswith(data1)

    def test03(self):
        password = "".join(randomutils.choices(string.ascii_letters, k=random.randint(4, 16)))
        cipher = cipherutils.S12Cipher(password=password)
        es = set()
        ps = set()
        for c in string.ascii_letters:
            d = cipher.encrypt(c)
            ps.add(c)
            es.add(d)
        assert len(ps) == len(es)


    def test04(self):
        gen = cipherutils.RawDataEncoder()
        data1 = os.urandom(1024)
        data2 = gen.encode(data1)
        data3 = gen.decode(data2)
        assert data1 == data3

    def test05(self):
        gen = cipherutils.HexlifyEncoder()
        data1 = os.urandom(1024)
        data2 = gen.encode(data1)
        data3 = gen.decode(data2)
        assert data1 == data3

        assert gen.encode(None) is None
        assert gen.decode(None) is None

    def test06(self):
        gen = cipherutils.Base64Encoder()
        data1 = os.urandom(1024)
        data2 = gen.encode(data1)
        data3 = gen.decode(data2)
        assert data1 == data3

        assert gen.encode(None) is None
        assert gen.decode(None) is None

    def test07(self):
        gen = cipherutils.SafeBase64Encoder()
        data1 = os.urandom(1024)
        data2 = gen.encode(data1)
        data3 = gen.decode(data2)
        assert data1 == data3

        assert gen.encode(None) is None
        assert gen.decode(None) is None

    def test08(self):
        cipher = cipherutils.S12Cipher(password="testpwd", result_encoder=cipherutils.HexlifyEncoder(), force_text=True)
        text1 = "".join(randomutils.choices(string.ascii_letters, k=1024))
        text2 = cipher.encrypt(text1)
        text3 = cipher.decrypt(text2)
        assert text1 == text3


    def test11(self):
        password = "".join(randomutils.choices(string.ascii_letters, k=random.randint(4, 16)))
        cipher = cipherutils.IvCipher(password=password)
        last_n2 = None
        for n1 in range(-10000, 10000, 100):
            n2 = cipher.encrypt(n1)
            n3 = cipher.decrypt(n2)
            if last_n2 is None:
                last_n2 = n2
            else:
                assert n2 > last_n2
            assert n1 == n3
            last_n2 = n2

    def test12(self):
        password = "".join(randomutils.choices(string.ascii_letters, k=random.randint(4, 16)))
        cipher = cipherutils.IvCipher(password=password)
        last_n2 = None
        for n1 in range(-10000, 10000, 100):
            n2 = cipher.encrypt(n1)
            n3 = cipher.decrypt(n2)
            if last_n2 is None:
                last_n2 = n2
            else:
                assert n2 > last_n2
            assert n1 == n3
            last_n2 = n2

    def test13(self):
        password = "".join(randomutils.choices(string.ascii_letters, k=random.randint(4, 16)))
        cipher = cipherutils.IvfCipher(password=password)
        n1 = 19231.1313
        n2 = cipher.encrypt(n1)
        n3 = cipher.decrypt(n2)
        assert n1 == n3

    def test14(self):
        for int_digits in range(1, 11):
            for float_digits in range(1, 6):
                for _ in range(5):
                    password = "".join(randomutils.choices(string.ascii_letters, k=random.randint(4, 16)))
                    cipher_params = {
                        "int_digits": int_digits,
                        "float_digits": float_digits,
                    }
                    cipher = cipherutils.IvfCipher(password=password, **cipher_params)
                    max_value = 10 ** int_digits + (1 - 0.1 ** float_digits)
                    range_start = -1 * max_value * (10 ** float_digits)
                    range_end = max_value * (10 ** float_digits)
                    ns = []
                    for n1 in range(int(range_start), int(range_end), int(range_end / 13)):
                        n1 /= (10 ** float_digits)
                        n2 = cipher.encrypt(n1)
                        n3 = cipher.decrypt(n2)
                        assert n1 == n3
                        ns.append(n2)
                    assert listutils.is_ordered(ns)

    def test15(self):
        for int_digits in range(1, 11):
            for _ in range(50):
                float_digits = 0
                password = "".join(randomutils.choices(string.ascii_letters, k=random.randint(4, 16)))
                cipher_params = {
                    "int_digits": int_digits,
                    "float_digits": float_digits,
                }
                cipher = cipherutils.IvfCipher(password=password, kwargs=cipher_params)
                max_value = 10 ** int_digits - random.randint(1, 1000)
                last_n2 = None
                for n1 in range(int(-1 * max_value), int(max_value), max(int(max_value / 13), 1)):
                    n2 = cipher.encrypt(n1)
                    n3 = cipher.decrypt(n2)
                    if last_n2 is None:
                        last_n2 = n2
                    else:
                        assert n2 > last_n2
                    assert n1 == n3
                    last_n2 = n2

    def test16(self):
        for i in range(0, 100):
            cipher = cipherutils.S1Cipher(password=os.urandom(8))
            data1 = os.urandom(1024)
            data2 = cipher.encrypt(data1)
            data3 = cipher.decrypt(data2)
            assert data1 == data3

    def test17(self):
        for i in range(0, 100):
            cipher = cipherutils.S2Cipher(password=os.urandom(8))
            data1 = os.urandom(1024)
            data2 = cipher.encrypt(data1)
            data3 = cipher.decrypt(data2)
            assert data1 == data3

    def test18(self):
        # Used for sorting test for S1Cipher
        # failed
        for loop1 in range(1):
            cipher = cipherutils.S1Cipher(password=os.urandom(16))
            for loop2 in range(100):
                data1 = os.urandom(random.randint(1, 100))
                data2 = os.urandom(random.randint(1, 100))
                flag1 = data1 > data2
                data3 = cipher.encrypt(data1)
                data4 = cipher.encrypt(data2)
                flag2 = data3 > data4
                #assert flag1 == flag2

    def test19(self):
        # Used for sorting test for S2Cipher
        # failed
        for loop1 in range(1):
            cipher = cipherutils.S2Cipher(password=os.urandom(16))
            for loop2 in range(100):
                data1 = os.urandom(random.randint(1, 100))
                data2 = os.urandom(random.randint(1, 100))
                flag1 = data1 > data2
                data3 = cipher.encrypt(data1)
                data4 = cipher.encrypt(data2)
                flag2 = data3 > data4
                #assert flag1 == flag2

    def test20(self):
        # Used for sorting test for S12Cipher
        # pass
        for loop1 in range(1):
            cipher = cipherutils.S12Cipher(password=os.urandom(16))
            for loop2 in range(100):
                data1 = os.urandom(random.randint(1, 100))
                data2 = os.urandom(random.randint(1, 100))
                flag1 = data1 > data2
                data3 = cipher.encrypt(data1)
                data4 = cipher.encrypt(data2)
                flag2 = data3 > data4
                assert flag1 == flag2

    def test21(self):
        # Used for partly searching test for S1Cipher with result_encoder=RawDataEncoder
        # pass
        for loop1 in range(1):
            password = os.urandom(16)
            cipher = cipherutils.S1Cipher(password=password)
            for loop2 in range(10):
                for x in range(256):
                    all_seeds = list(range(256))
                    all_seeds.remove(x)
                    random.shuffle(all_seeds)
                    data = cipher.encrypt(bytes(all_seeds))
                    xt = cipher.encrypt(bytes([x]))
                    assert not xt in data

    def test22(self):
        # Used for partly searching test for S1Cipher with result_encoder=HexlifyEncoder
        # failed
        for loop1 in range(1):
            password = os.urandom(16)
            cipher = cipherutils.S1Cipher(password=password, result_encoder=cipherutils.HexlifyEncoder())
            for loop2 in range(10):
                for x in range(256):
                    all_seeds = list(range(256))
                    all_seeds.remove(x)
                    random.shuffle(all_seeds)
                    data = cipher.encrypt(bytes(all_seeds))
                    xt = cipher.encrypt(bytes([x]))
                    #assert not xt in data

    def test23(self):
        # Used for partly searching test for S2Cipher with result_encoder=Utf8Encoder
        # failed
        for loop1 in range(1):
            password = os.urandom(16)
            cipher = cipherutils.S2Cipher(password=password)
            for loop2 in range(10):
                for x in range(256):
                    all_seeds = list(range(256))
                    all_seeds.remove(x)
                    random.shuffle(all_seeds)
                    data = cipher.encrypt(bytes(all_seeds))
                    xt = cipher.encrypt(bytes([x]))
                    #assert not xt in data

    def test24(self):
        # Used for partly searching test for S2Cipher with result_encoder=HexlifyEncoder
        # failed
        for loop1 in range(1):
            password = os.urandom(16)
            cipher = cipherutils.S2Cipher(password=password, result_encoder=cipherutils.HexlifyEncoder())
            for loop2 in range(10):
                for x in range(256):
                    all_seeds = list(range(256))
                    all_seeds.remove(x)
                    random.shuffle(all_seeds)
                    data = cipher.encrypt(bytes(all_seeds))
                    xt = cipher.encrypt(bytes([x]))
                    #assert not xt in data

    def test25(self):
        # Used for partly searching test for S12Cipher with result_encoder=RawDataEncoder
        # failed
        for loop1 in range(1):
            password = os.urandom(16)
            cipher = cipherutils.S12Cipher(password=password)
            for loop2 in range(10):
                for x in range(256):
                    all_seeds = list(range(256))
                    all_seeds.remove(x)
                    random.shuffle(all_seeds)
                    data = cipher.encrypt(bytes(all_seeds))
                    xt = cipher.encrypt(bytes([x]))
                    #assert not xt in data

    def test26(self):
        # Used for partly searching test for S12Cipher with result_encoder=HexlifyEncoder
        # failed
        for loop1 in range(1):
            password = os.urandom(16)
            cipher = cipherutils.S12Cipher(password=password, result_encoder=cipherutils.HexlifyEncoder())
            for loop2 in range(10):
                for x in range(256):
                    all_seeds = list(range(256))
                    all_seeds.remove(x)
                    random.shuffle(all_seeds)
                    data = cipher.encrypt(bytes(all_seeds))
                    xt = cipher.encrypt(bytes([x]))
                    #assert not xt in data


    def test29(self):
        thelist = []
        for i in range(1000000000000000, 1000000000000000+10):
            cipher = cipherutils.IvfCipher(password="testpwd")
            value = cipher.encrypt(i)
            thelist.append(value)
        assert listutils.is_ordered(thelist)

    def test30(self):
        c1 = cipherutils.S1Cipher(password="hello")
        c2 = cipherutils.S1Cipher(password="hello")
        d1 = c1.encrypt("hello")
        d2 = c2.encrypt("hello")
        assert d1 == d2

    def test31(self):
        c1 = cipherutils.S2Cipher(password="hello")
        c2 = cipherutils.S2Cipher(password="hello")
        d1 = c1.encrypt("hello")
        d2 = c2.encrypt("hello")
        assert d1 == d2

    def test32(self):
        c1 = cipherutils.S12Cipher(password="hello")
        c2 = cipherutils.S12Cipher(password="hello")
        d1 = c1.encrypt("hello")
        d2 = c2.encrypt("hello")
        assert d1 == d2

    def test33(self):
        c1 = cipherutils.S1Cipher(password="hello")
        d1 = c1.encrypt("hello")
    
        password = c1.dumps()
        c2 = cipherutils.S1Cipher(password=password)
        d2 = c2.encrypt("hello")
        assert d1 == d2

    def test34(self):
        c1 = cipherutils.S2Cipher(password="hello")
        d1 = c1.encrypt("hello")
    
        password = c1.dumps()
        c2 = cipherutils.S2Cipher(password=password)
        d2 = c2.encrypt("hello")
        assert d1 == d2

    def test35(self):
        c1 = cipherutils.S12Cipher(password="hello")
        d1 = c1.encrypt("hello")
    
        password = c1.dumps()
        c2 = cipherutils.S12Cipher(password=password)
        d2 = c2.encrypt("hello")
        assert d1 == d2

    def test36(self):
        gen = cipherutils.Utf8Encoder()
        data1 = "测试".encode("utf-8")
        data2 = gen.encode(data1)
        data3 = gen.decode(data2)
        assert data1 == data3

        assert gen.encode(None) is None
        assert gen.decode(None) is None

    def test37(self):
        for i in range(0, 100):
            password = os.urandom(8)
            cipher1 = cipherutils.S1Cipher(password=password)
            key = cipherutils.S1Cipher.password_to_key(password)
            cipher2 = cipherutils.S1Cipher(password=key)

            data1 = os.urandom(1024)
            data2 = cipher1.encrypt(data1)
            data3 = cipher2.decrypt(data2)
            assert data1 == data3

    def test38(self):
        for i in range(0, 100):
            password = os.urandom(8)
            cipher1 = cipherutils.S1Cipher(password=password)
            cipher2 = cipherutils.S1Cipher(password=password)

            data1 = os.urandom(1024)
            data2 = cipher1.encrypt(data1)
            data3 = cipher2.decrypt(data2)
            assert data1 == data3

    def test39(self):
        for i in range(0, 100):
            length = random.randint(8, 128)
            password = os.urandom(length)
            cipher1 = cipherutils.S1Cipher(password=password)
            key = cipherutils.S1Cipher.password_to_key(password)
            cipher2 = cipherutils.S1Cipher(password=key)
            assert cipher1.seeds == cipher2.seeds
