#!/usr/bin/env python
# -*- coding: utf8 -*-
"""加解密工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
import json
import binascii
import string
from . import strutils
from . import base64utils
from . import randomutils
from . import listutils
from . import funcutils
from . import numericutils
from .sixutils import force_bytes
from .sixutils import bytes_to_array
from .sixutils import force_text

__all__ = [
    "DecryptFailed",
    "EncoderBase",
    "RawDataEncoder",
    "HexlifyEncoder",
    "Base64Encoder",
    "SafeBase64Encoder",
    "Utf8Encoder",
    "CipherBase",
    "IvCipher",
    "IvfCipher",
    "MappingCipher",
    "S1Cipher",
    "S2Cipher",
    "S12Cipher",
]


class DecryptFailed(RuntimeError):
    """decrypt failed error."""


class EncoderBase(object):
    """Result encoder base."""

    def encode(self, data):
        """Encode result data."""
        raise NotImplementedError()

    def decode(self, data):
        """Decode result data."""
        raise NotImplementedError()


class RawDataEncoder(EncoderBase):
    """Use raw data as result data."""

    def encode(self, data):
        return data

    def decode(self, data):
        return data


class HexlifyEncoder(EncoderBase):
    """Hexlify the result data."""

    def encode(self, data):
        if data is None:
            return None
        return binascii.hexlify(data).decode()

    def decode(self, data):
        if data is None:
            return None
        return binascii.unhexlify(data.encode("utf-8"))


class Base64Encoder(EncoderBase):
    """Base64 encode the result data."""

    def encode(self, data):
        if data is None:
            return None
        data = force_bytes(data)
        return strutils.join_lines(strutils.force_text(base64utils.encodebytes(data)))

    def decode(self, data):
        if data is None:
            return None
        data = strutils.force_bytes(data)
        return base64utils.decodebytes(data)


class SafeBase64Encoder(EncoderBase):
    """Safe base64 encode the result data."""

    def encode(self, data):
        if data is None:
            return None
        data = force_bytes(data)
        return strutils.join_lines(
            strutils.force_text(base64utils.urlsafe_b64encode(data))
        )

    def decode(self, data):
        if data is None:
            return None
        data = force_bytes(data)
        return base64utils.urlsafe_b64decode(data)


class Utf8Encoder(EncoderBase):
    """utf8 encode the result data."""

    def encode(self, data):
        """Turn utf8 decodable bytes to string.

        @Returns:
            (str): The result string.

        @Parameters:
            data(bytes): Utf8 decodable bytes.

        @Example:
            encoder = Utf8Encoder()
            data1 = "测试".encode("utf-8")
            data2 = encoder.encode(data1)
            data3 = encoder.decode(data2)
            assert data1 == data3
            assert data2 = "测试"
        """
        if not data:
            return None
        return data.decode("utf-8")

    def decode(self, data):
        """Turn utf8 encodable str to utf8 encoded bytes.

        @Returns:
            (bytes): The result bytes.

        @Parameters:
            data(str): Utf8 encodable str.

        @Example:
            encoder = Utf8Encoder()
            data1 = "测试".encode("utf-8")
            data2 = encoder.encode(data1)
            data3 = encoder.decode(data2)
            assert data1 == data3
            assert data2 = "测试"
        """
        if not data:
            return None
        return data.encode("utf-8")


class _SimpleCipher(object):
    def __init__(self, encrypt, decrypt):
        self.encrypt = encrypt
        self.decrypt = decrypt


class CipherBase(object):
    """params: password, result_encoder, force_text, text_encoding, cipher_core, encrypt, decrypt, encrypt_kwargs, decrypt_kwargs"""

    default_encrypt_force_bytes = True
    default_decrypt_force_bytes = True
    default_encrypt_kwargs = {}
    default_decrypt_kwargs = {}
    default_result_encoder = None
    default_force_text = None
    default_text_encoding = None
    default_cipher_core = None

    def get_defaults(self):
        defaults = {
            "encrypt_force_bytes": self.default_encrypt_force_bytes,
            "decrypt_force_bytes": self.default_decrypt_force_bytes,
            "encrypt_kwargs": self.default_encrypt_kwargs,
            "decrypt_kwargs": self.default_decrypt_kwargs,
            "result_encoder": self.default_result_encoder,
            "force_text": self.default_force_text,
            "text_encoding": self.default_text_encoding,
            "cipher_core": self.default_cipher_core,
        }
        if hasattr(self, "defaults"):
            defaults.update(getattr(self, "defaults"))
        return defaults

    def __init__(
        self,
        password=None,
        encrypt_force_bytes=None,
        decrypt_force_bytes=None,
        encrypt_kwargs=None,
        decrypt_kwargs=None,
        result_encoder=None,
        force_text=None,
        text_encoding=None,
        cipher_core=None,
        encrypt=None,
        decrypt=None,
        kwargs=None,
        **extra_kwargs
    ):
        kwargs = kwargs or {}
        defaults = self.get_defaults()
        self.password = password
        self.encrypt_force_bytes = listutils.first(
            encrypt_force_bytes, defaults["encrypt_force_bytes"], True
        )
        self.decrypt_force_bytes = listutils.first(
            decrypt_force_bytes, defaults["decrypt_force_bytes"], True
        )
        self.result_encoder = listutils.first(
            result_encoder, defaults["result_encoder"], RawDataEncoder()
        )
        self.force_text = listutils.first(force_text, defaults["force_text"], False)
        self.text_encoding = listutils.first(
            text_encoding, defaults["text_encoding"], "utf-8"
        )
        self.cipher_core = listutils.first(cipher_core, defaults["cipher_core"], None)
        self.encrypt_kwargs = listutils.first(
            encrypt_kwargs, defaults["encrypt_kwargs"], {}
        )
        self.decrypt_kwargs = listutils.first(
            decrypt_kwargs, defaults["decrypt_kwargs"], {}
        )
        for key, value in kwargs.items():
            self.encrypt_kwargs.setdefault(key, value)
            self.decrypt_kwargs.setdefault(key, value)
        self.kwargs = extra_kwargs
        self.cipher_instance = None
        if self.cipher_core:
            self.cipher_instance = funcutils.call_with_inject(
                self.cipher_core, self.kwargs
            )
        else:
            if encrypt or decrypt:
                self.cipher_instance = _SimpleCipher(encrypt, decrypt)

    def encrypt(self, data, **kwargs):
        if data is None:
            return None
        if self.encrypt_force_bytes:
            data = strutils.force_bytes(data, self.text_encoding)
        encrypted_data = self.do_encrypt(data, **kwargs)
        return self.result_encoder.encode(encrypted_data)

    def decrypt(self, text, **kwargs):
        if text is None:
            return None
        data = self.result_encoder.decode(text)
        if self.decrypt_force_bytes:
            data = strutils.force_bytes(data, self.text_encoding)
        decrypted_data = self.do_decrypt(data, **kwargs)
        if self.force_text:
            return strutils.force_text(decrypted_data, self.text_encoding)
        else:
            return decrypted_data

    def do_encrypt(self, data, **kwargs):
        if self.cipher_instance:
            context = {}
            context.update(self.encrypt_kwargs)
            context.update(kwargs)
            return self.cipher_instance.encrypt(data, **context)
        else:
            raise NotImplementedError("No encrypt method...")

    def do_decrypt(self, data, **kwargs):
        if self.cipher_instance:
            context = {}
            context.update(self.decrypt_kwargs)
            context.update(kwargs)
            return self.cipher_instance.decrypt(data, context)
        else:
            return NotImplementedError("NO decrypt method...")


class IvCipher(CipherBase):
    """Int value encryption and decryption cipher.

    Example:

    In [38]: from fastutils import cipherutils

    In [39]: cipher = cipherutils.IvCipher(password='hello')

    In [40]: for i in range(10):
        ...:     print(i, cipher.encrypt(i))
        ...:
    0 0
    1 97
    2 112
    3 204
    4 205
    5 253
    6 294
    7 339
    8 364
    9 447
    """

    default_encrypt_force_bytes = False
    default_decrypt_force_bytes = False

    def __init__(self, password, **kwargs):
        self.password = password
        self.iv_params = self.get_iv_params()
        super(IvCipher, self).__init__(passowrd=password, **kwargs)

    def get_iv_params(self):
        gen = randomutils.Random(self.password)
        n = gen.randint(1024, 9999)
        iv = [gen.randint(1, 100) for _ in range(n)]
        return n, iv

    def do_encrypt(self, number, **kwargs):
        number = strutils.force_int(number)
        flag = False
        if number < 0:
            number = -1 * number
            flag = True
        n, iv = self.iv_params
        s = sum(iv)
        a = number // n
        b = number % n
        r = a * s + sum(iv[:b])
        if flag:
            r = -1 * r
        return r

    def do_decrypt(self, number, **kwargs):
        number = strutils.force_int(number)
        flag = False
        if number < 0:
            number = -1 * number
            flag = True
        n, iv = self.iv_params
        s = sum(iv)
        a = number // s
        t = s * a
        if t == number:
            r = a * n
        else:
            for delta in range(n):
                t += iv[delta]
                if t == number:
                    r = a * n + delta + 1
                    break
            if t != number:
                raise DecryptFailed("iv_decrypt failed: number={}".format(number))
        if flag:
            r = -1 * r
        return r


class IvfCipher(IvCipher):
    """Float value encryption and decryption cipher.

    Example:

    In [41]: from fastutils import cipherutils

    In [42]: cipher = cipherutils.IvfCipher(password='hello')

    In [43]: for i in range(10):
        ...:     print(i, cipher.encrypt(i), type(cipher.encrypt(i)))
        ...:
        ...:
    0 +0000000000000000000000 <class 'str'>
    1 +0000000000005004032834 <class 'str'>
    2 +0000000000010008064455 <class 'str'>
    3 +0000000000015012094180 <class 'str'>
    4 +0000000000020016127691 <class 'str'>
    5 +0000000000025020160338 <class 'str'>
    6 +0000000000030024191109 <class 'str'>
    7 +0000000000035028221552 <class 'str'>
    8 +0000000000040032254031 <class 'str'>
    9 +0000000000045036286491 <class 'str'>
    """

    def __init__(self, password, int_digits=12, float_digits=4, **kwargs):
        """password is required.
        int_digits is the max length of int part value. Add 0 padding to left.
        float_digits is the max length of float part value. Add 0 padding to right.
        """
        self.int_digits = int_digits
        self.float_digits = float_digits
        self.module = 10 ** (float_digits * 2)
        self.max_value_length = float_digits * 2 + self.int_digits + 2
        self.max = 10**self.max_value_length - 1
        self.value_template = "{:0%dd}" % self.max_value_length
        super(IvfCipher, self).__init__(password=password, **kwargs)

    def do_encrypt(self, number, **kwargs):
        number = int(number * self.module)
        number = super(IvfCipher, self).do_encrypt(number)
        if number >= 0:
            return "+" + self.value_template.format(number)
        else:
            return "*" + self.value_template.format(self.max - abs(number))

    def do_decrypt(self, number, **kwargs):
        sign = number[0]
        number = int(number[1:])
        if sign == "*":
            number = self.max - number
        number = super(IvfCipher, self).do_decrypt(number)
        number = round(number / self.module, self.float_digits)
        if self.float_digits == 0:
            number = int(number)
        if sign == "*":
            return -1 * number
        else:
            return number


class MappingCipher(CipherBase):
    """Turn every byte to another value.

    0 -> b'randseed01'
    1 -> b'randseed02'
    ... -> ...
    255 -> b'randseed03'

    """

    def __init__(self, password=None, **kwargs):
        super(MappingCipher, self).__init__(password=password, **kwargs)
        self.password = password
        self.seeds = self.try_to_load_seeds(password)
        if not self.seeds:
            self.randomGenerator = randomutils.Random(password)
            self.seeds = self.get_seeds()
        self.encrypt_mapping = self.get_encrypt_mapping()
        self.decrypt_mapping = self.get_decrypt_mapping()

    def get_seeds(self):
        raise NotImplementedError()

    def get_encrypt_mapping(self):
        mapping = {}
        for i in range(256):
            mapping[numericutils.int2bytes(i)] = self.seeds[i]
        return mapping

    def get_decrypt_mapping(self):
        mapping = {}
        for i in range(256):
            mapping[self.seeds[i]] = numericutils.int2bytes(i)
        return mapping

    def do_encrypt(self, data, **kwargs):
        if data is None:
            return None
        data = bytes_to_array(data)
        empty = b""
        result = empty.join([self.encrypt_mapping[c] for c in data])
        return result

    def do_decrypt(self, data, **kwargs):
        if data is None:
            return None
        result = b""
        data_length = len(data)
        max_seed_length = max([len(x) for x in self.decrypt_mapping.keys()])
        start = 0
        while start < data_length:
            found = False
            for seed_length in range(1, max_seed_length + 1):
                seed = data[start : start + seed_length]
                if seed in self.decrypt_mapping:
                    result += self.decrypt_mapping[seed]
                    start += seed_length
                    found = True
                    break
            if not found:
                raise DecryptFailed()
        return result

    def dumps(self):
        seeds = [binascii.hexlify(x).decode() for x in self.seeds]
        data = strutils.force_bytes(json.dumps(seeds))
        data = strutils.force_text(binascii.hexlify(data))
        return data

    @classmethod
    def loads(cls, data):
        return cls(password=data)

    @classmethod
    def try_to_load_seeds(cls, data):
        try:
            data = force_bytes(data)
            data = binascii.unhexlify(data)
            data = force_text(data)
            seeds = json.loads(data)
            seeds = [binascii.unhexlify(force_bytes(x)) for x in seeds]
            return seeds
        except Exception:
            return None

    @classmethod
    def password_to_key(cls, password):
        cipher = cls(password=password)
        return cipher.dumps()


class S1Cipher(MappingCipher):
    """Turn every byte to another byte randomly by the password.

    b'\x00' -> b'\x8f'
    b'\x01' -> b'\x8d'
    ...
    b'\xff' -> b'\xd8'
    """

    def get_seeds(self):
        seeds = list(range(256))
        self.randomGenerator.shuffle(seeds)
        return [numericutils.int2bytes(x) for x in seeds]


class S2Cipher(MappingCipher):
    """Turn every byte to two ascii_lowercase str randomly by the password.

    b'\x00' -> "si"
    b'\x01' -> "xs"
    ...
    b'\xff' -> "xy"
    """

    def get_seeds(self):
        letters = string.ascii_lowercase
        seeds = set()
        for a in letters:
            for b in letters:
                seeds.add(a + b)
        seeds = list(seeds)
        self.randomGenerator.shuffle(seeds)
        seeds = [x.encode() for x in seeds[:256]]
        return seeds


class S12Cipher(MappingCipher):
    """Turn every byte to two random bytes that keeps the order.

    b'\x00' -> b"\x01\x0d"
    b'\x01' -> b"\x01\x1a"
    ...
    b'\xff' -> b"\xef\xcc"
    """

    def get_seeds(self):
        v = randomutils.Random(self.password).get_bytes(256)
        v = strutils.bytes2ints(v)
        values = list(range(256))
        delta = 0
        for index in range(256):
            delta += v[index]
            values[index] += delta
        seeds = []
        for code in range(256):
            value = values[code]
            high = value // 256
            low = value % 256
            seeds.append(strutils.ints2bytes([high, low]))
        return seeds
