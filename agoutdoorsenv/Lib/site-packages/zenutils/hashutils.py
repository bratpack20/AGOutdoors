#!/usr/bin/env python
# -*- coding: utf8 -*-
"""哈希工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

from . import strutils
from . import base64utils
from . import numericutils
from .sixutils import TEXT
from .sixutils import BYTES
from .sixutils import BYTES_TYPE
from .sixutils import STR_TYPE
from .sixutils import force_bytes
from .sixutils import force_text
from .sixutils import create_new_class

import os
import binascii

__all__ = [
    "algorithms_available",
    "ResultEncoderBase",
    "DigestResultEncoder",
    "Base64ResultEncoder",
    "HexlifyResultEncoder",
    "setup_hash_method_loader",
    "method_load",
    "new",
    "is_the_same_hash_method",
    "pbkdf2_hmac",
    "get_file_hash_result",
    "get_hash_result",
    "get_salted_hash_base64",
    "get_pbkdf2_hmac",
    "validate_pbkdf2_hmac",
    "PasswordHashMethodNotSupportError",
    "PasswordHashMethodBase",
    "register_password_hash_method",
    "get_password_hash_methods",
    "get_password_hash",
    "validate_password_hash",
    "Pbkdf2PasswordHashBase",
    "register_pbkdf2_password_hash",
    "SimplePasswordHashBase",
    "register_simple_password_hash",
    "SimpleSaltPasswordHashBase",
    "register_simple_salt_password_hash",
    "HexlifyPasswordHashBase",
    "register_hexlify_password_hash",
    "get_file_hash",
    "get_file_hash_hexdigest",
    "get_file_hash_base64",
    "get_hash",
    "get_hash_digest",
    "get_hash_hexdigest",
    "get_hash_base64",
]

import re
import logging
import string
import hashlib
import functools

# ##################################################################################
# GLOBAL VARIABLES AREA
# ##################################################################################
logger = logging.getLogger(__name__)

algorithms_available = set()
algorithms_name_mapping = {}
for _method_name in hashlib.algorithms_guaranteed:
    _method_name_lower = _method_name.lower()
    _method_name_lower = _method_name_lower.replace("-", "_")
    algorithms_available.add(_method_name_lower)
    algorithms_name_mapping[_method_name_lower] = _method_name

DEFAULT_HASH_METHOD = "sm3"
DEFAULT_PASSWORD_HASH_METHOD = "ssm3"
DEFAULT_BUFFER_SIZE = 1024 * 1024


# ##################################################################################
# RESULT ENCODER AREA
# ##################################################################################
class ResultEncoderBase(object):
    """哈希值编解码工具基类。"""

    @classmethod
    def encode(cls, result):
        """编码"""
        raise NotImplementedError()

    @classmethod
    def decode(cls, result):
        "解码"
        raise NotImplementedError()


class DigestResultEncoder(ResultEncoderBase):
    """使用原始二进制值，不进行编解码操作。"""

    @classmethod
    def encode(cls, result):
        return result

    @classmethod
    def decode(cls, result):
        return result


class Base64ResultEncoder(ResultEncoderBase):
    """Base64编解码工具类。"""

    @classmethod
    def encode(cls, result):
        return strutils.join_lines(TEXT(base64utils.encodebytes(result)))

    @classmethod
    def decode(cls, result):
        return base64utils.decodebytes(BYTES(result))


class HexlifyResultEncoder(ResultEncoderBase):
    """十六进制编解码工具类。"""

    @classmethod
    def encode(cls, result):
        return TEXT(binascii.hexlify(result))

    @classmethod
    def decode(cls, result):
        return binascii.unhexlify(BYTES(result))


DEFAULT_RESULT_ENCODER = HexlifyResultEncoder

# ##################################################################################
# HASH METHOD LOADER BASE AREA
# ##################################################################################
HASH_METHOD_LOADERS = {}


def setup_hash_method_loader(name, loader):
    algorithms_available.add(name)
    HASH_METHOD_LOADERS[name] = loader


def new(method, *args, **kwargs):
    """New hash generator instance."""
    method = method.lower().strip()
    if method in HASH_METHOD_LOADERS:
        return method_load(method)(*args, **kwargs)
    else:
        method = algorithms_name_mapping.get(method, method)
        return hashlib.new(method, *args, **kwargs)


def method_load(method):
    """Get hash generator class by method name.

    @Returns:
        (hash generator class)

    @Parameters:
        method(str, bytes, hash generator class): Hash generator class name.
    """
    if isinstance(method, (BYTES_TYPE, STR_TYPE)):
        method = force_text(method)
        loader = HASH_METHOD_LOADERS.get(method, None)
        if loader:
            return loader()
        else:
            return lambda: new(method)
    else:
        return method


def is_the_same_hash_method(method1, method2):
    """Use a random buffer hash code to test if the method1 and method2 are the same hash method."""
    buffer = os.urandom(1024)
    gen1 = method1()
    gen2 = method2()
    gen1.update(buffer)
    gen2.update(buffer)
    return gen1.digest() == gen1.digest()


# ##################################################################################
# HASH METHOD LOADER REGISTER AREA
# ##################################################################################
_hashlib_has_sm3_flag = None


def get_sm3_class():
    """
    load sm3 class from sm3utils.
    zenutils is not deps on sm3utils, so you need to install sm3utils by yourself.
    """
    global _hashlib_has_sm3_flag
    if _hashlib_has_sm3_flag is None:
        try:
            hashlib.new("sm3")
            _hashlib_has_sm3_flag = True
        except:
            _hashlib_has_sm3_flag = False
    if _hashlib_has_sm3_flag:
        return lambda: hashlib.new("sm3")
    else:
        try:
            from sm3utils import sm3
        except ImportError:
            msg = "Sm3 in not avaiable in hashlib of your python installation. We need a third party library sm3utils, which is not a part of zenutils. You need to installed sm3utils by yourself, or put it into your project's requirements.txt."
            logger.error(msg)
            raise RuntimeError(msg)
        return sm3


def get_sha_class():
    """
    alias sha1 as sha
    """
    return lambda: hashlib.new("sha1")


def get_xxh128_class():
    try:
        from xxhash import xxh128
    except ImportError:
        msg = "xxh128 hash requires library xxhash, which is not a part of zenutils. You need to installed xxhash by yourself, or put it into your project's requirements.txt."
        logger.error(msg)
        raise RuntimeError(msg)
    return xxh128


def get_xxh64_class():
    try:
        from xxhash import xxh64
    except ImportError:
        msg = "xxh64 hash requires library xxhash, which is not a part of zenutils. You need to installed xxhash by yourself, or put it into your project's requirements.txt."
        logger.error(msg)
        raise RuntimeError(msg)
    return xxh64


def get_xxh32_class():
    try:
        from xxhash import xxh32
    except ImportError:
        msg = "xxh32 hash requires library xxhash, which is not a part of zenutils. You need to installed xxhash by yourself, or put it into your project's requirements.txt."
        logger.error(msg)
        raise RuntimeError(msg)
    return xxh32


setup_hash_method_loader("sha", get_sha_class)
setup_hash_method_loader("sm3", get_sm3_class)
setup_hash_method_loader("xxh128", get_xxh128_class)
setup_hash_method_loader("xxh64", get_xxh64_class)
setup_hash_method_loader("xxh32", get_xxh32_class)


# ##################################################################################
# PBKDF2 HMAC HANDLER AERA
# ##################################################################################
def _pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None):
    """Password based key derivation function 2 (PKCS #5 v2.0)

    This Python implementations based on the hmac module about as fast
    as OpenSSL's PKCS5_PBKDF2_HMAC for short passwords and much faster
    for long passwords.
    """

    _trans_5C = numericutils.ints2bytes((x ^ 0x5C) for x in range(256))
    _trans_36 = numericutils.ints2bytes((x ^ 0x36) for x in range(256))

    if not isinstance(hash_name, STR_TYPE):
        msg = "hash_name {value} requires {required_type} type but got {real_type} type...".format(
            value=hash_name,
            required_type=STR_TYPE,
            real_type=type(hash_name),
        )
        raise TypeError(msg)

    if not isinstance(password, (bytes, bytearray)):
        password = bytes(memoryview(password))
    if not isinstance(salt, (bytes, bytearray)):
        salt = bytes(memoryview(salt))

    # Fast inline HMAC implementation
    inner = new(hash_name)
    outer = new(hash_name)
    blocksize = getattr(inner, "block_size", 64)
    if len(password) > blocksize:
        password = new(hash_name, password).digest()
    password = password + b"\x00" * (blocksize - len(password))
    inner.update(password.translate(_trans_36))
    outer.update(password.translate(_trans_5C))

    def prf(msg, inner=inner, outer=outer):
        # PBKDF2_HMAC uses the password as key. We can re-use the same
        # digest objects and just update copies to skip initialization.
        icpy = inner.copy()
        ocpy = outer.copy()
        icpy.update(msg)
        ocpy.update(icpy.digest())
        return ocpy.digest()

    if iterations < 1:
        raise ValueError(iterations)
    if dklen is None:
        dklen = outer.digest_size
    if dklen < 1:
        raise ValueError(dklen)

    dkey = b""
    loop = 1
    from_bytes = numericutils.from_bytes
    while len(dkey) < dklen:
        # prev = prf(salt + loop.to_bytes(4, 'big'))
        prev = prf(salt + numericutils.int2bytes(loop, 4, "big"))
        # endianness doesn't matter here as long to / from use the same
        rkey = from_bytes(prev, "big")
        for i in range(iterations - 1):
            prev = prf(prev)
            # rkey = rkey ^ prev
            rkey ^= from_bytes(prev, "big")
        loop += 1
        # dkey += rkey.to_bytes(inner.digest_size, 'big')
        dkey += numericutils.int2bytes(rkey, inner.digest_size, "big")
    return dkey[:dklen]


# ##################################################################################
#
# FIX hashlib.pbkdf2_hmac missing problem for old python
#
# But because hashlib.pbkdf2_hmac is not support extra hash method
# So better not use hashlib.pbkdf2_hmac directly
# You can use pbkdf2_hmac to work with your self define hash method
# Firstly you have to register your self define hash method with setup_hash_method_loader
#
# ##################################################################################
def pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None):
    """If method supported by hashlib, returns hashlib.pbkdf2_hmac, or else returns self defined _pbkdf2_hmac."""
    try:
        return hashlib.pbkdf2_hmac(hash_name, password, salt, iterations, dklen)
    except AttributeError:
        return _pbkdf2_hmac(hash_name, password, salt, iterations, dklen)
    except ValueError:
        return _pbkdf2_hmac(hash_name, password, salt, iterations, dklen)


# ##################################################################################
# BASE HASH CALC AREA
# ##################################################################################


def get_file_hash_result(filename, **kwargs):
    method = kwargs.get("method", DEFAULT_HASH_METHOD)
    buffer_size = kwargs.get("buffer_size", DEFAULT_BUFFER_SIZE)
    result_encoder = kwargs.get("result_encoder", DEFAULT_RESULT_ENCODER)
    method = method_load(method)
    gen = method()
    with open(filename, "rb") as fobj:
        while True:
            buffer = fobj.read(buffer_size)
            if not buffer:
                break
            gen.update(buffer)
    digest = gen.digest()
    return result_encoder.encode(digest)


def get_hash_result(*args, **kwargs):
    method = kwargs.get("method", DEFAULT_HASH_METHOD)
    result_encoder = kwargs.get("result_encoder", DEFAULT_RESULT_ENCODER)
    gen_class = method_load(method)
    gen = gen_class()
    for arg in args:
        gen.update(force_bytes(arg))
    digest = gen.digest()
    return result_encoder.encode(digest)


def get_salted_hash_base64(*args, **kwargs):
    method = kwargs.get("method", "md5")
    salt_length = kwargs.get("salt_length", 4)
    salt = kwargs.get("salt", None)
    if salt is None:
        salt = strutils.random_string(length=salt_length)
    gen_class = method_load(method)
    gen = gen_class()
    for arg in args:
        gen.update(force_bytes(arg))
    gen.update(force_bytes(salt))
    data = gen.digest() + force_bytes(salt)
    result = force_text(base64utils.encodebytes(data))
    return strutils.join_lines(result)


# ##################################################################################
# PBKDF2 HMAC CALC AREA
# ##################################################################################


def get_pbkdf2_hmac(
    text,
    salt=None,
    iterations=2048,
    hash_name=DEFAULT_HASH_METHOD,
    seperator_between_pbkdf2_and_method="_",
):
    if salt is None:
        salt = strutils.random_string(16, choices=string.ascii_letters)
    text = force_bytes(text)
    salt = force_bytes(salt)
    data = pbkdf2_hmac(hash_name, text, salt, iterations)
    return "pbkdf2{seperator}{hash_name}${iterations}${salt}${data}".format(
        seperator=seperator_between_pbkdf2_and_method,
        hash_name=TEXT(hash_name),
        iterations=iterations,
        salt=TEXT(salt),
        data=strutils.join_lines(TEXT(base64utils.encodebytes(data))),
    )


def validate_pbkdf2_hmac(password, text):
    text = force_text(text)
    matches = re.findall("pbkdf2([_:])(.+)\\$(\\d+)\\$(.+)\\$(.+)", text)
    if len(matches) != 1:
        return False
    sep, hash_name, iterations, salt, _ = matches[0]
    if not iterations.isdigit():
        return False
    else:
        iterations = int(iterations)
    data = get_pbkdf2_hmac(
        password,
        salt=salt,
        iterations=iterations,
        hash_name=hash_name,
        seperator_between_pbkdf2_and_method=sep,
    )
    if data == text:
        return True
    else:
        return False


# ##################################################################################
# PASSWORD HASH AREA
# ##################################################################################
PASSWORD_HASH_METHODS = {}


class PasswordHashMethodNotSupportError(Exception):
    pass


class PasswordHashMethodBase(object):
    def get_password_hash(self, password):
        pass

    def validate_password_hash(self, password_hash_data, password):
        pass


def register_password_hash_method(name, password_hash_method_instance):
    PASSWORD_HASH_METHODS[name] = password_hash_method_instance


def get_password_hash_methods():
    methods = list(PASSWORD_HASH_METHODS.keys())
    methods.sort()
    return methods


def get_password_hash(password, method=DEFAULT_PASSWORD_HASH_METHOD):
    """
    4 kind password hash format supported:

    1. Simple hash with method prefix. e.g. {SHA1}w0mcJylzCn+AfvuGdqkty2+KP48=
    2. Salted hash with method prefix. e.g. {SSHA}qWgORjfMmQJPipkl0KtdvQ6rGcppdVBIZGtGcQ==
    3. Pbkdf2 hmac hash. e.g. 'pbkdf2_sha256$2048$TdisEdeyNKNltWAj$eLzCMpQjSDIh9GFMjJCzhBPexrfeQfoLYypbHtTH6V8='
    4. Simple hash in hex digest. e.g. c3499c2729730a7f807efb8676a92dcb6f8a3f8f.
    """
    method = method.upper()
    password_hash_method = PASSWORD_HASH_METHODS.get(method, None)
    if password_hash_method:
        return password_hash_method.get_password_hash(password)
    else:
        raise PasswordHashMethodNotSupportError()


def validate_password_hash(password_hash_data, password):
    for _, method in PASSWORD_HASH_METHODS.items():
        result = method.validate_password_hash(password_hash_data, password)
        if result in [True, False]:
            return result
    return False


class Pbkdf2PasswordHashBase(PasswordHashMethodBase):
    seperator_between_pbkdf2_and_method = "_"
    method = DEFAULT_HASH_METHOD
    prefix = "pbkdf2_{method}$".format(method=DEFAULT_HASH_METHOD)

    def get_password_hash(self, password):
        return get_pbkdf2_hmac(
            password,
            hash_name=self.method,
            seperator_between_pbkdf2_and_method=self.seperator_between_pbkdf2_and_method,
        )

    def validate_password_hash(self, password_hash_data, password):
        if not hasattr(self, "prefix"):
            return None
        if not password_hash_data.startswith(self.prefix):
            return None
        return validate_pbkdf2_hmac(password, password_hash_data)


def register_pbkdf2_password_hash(method, prefix, seperator, class_name_suffix=""):
    class_name = "".join(
        [x.title() for x in [method, "pbkdf2", "password", "hash", class_name_suffix]]
    )
    globals()[class_name] = create_new_class(
        class_name,
        (Pbkdf2PasswordHashBase,),
        {
            "seperator_between_pbkdf2_and_method": seperator,
            "method": method,
            "prefix": prefix,
        },
    )
    return globals()[class_name]


class SimplePasswordHashBase(PasswordHashMethodBase):
    method = DEFAULT_PASSWORD_HASH_METHOD
    prefix = "{{{method}}}".format(method=DEFAULT_PASSWORD_HASH_METHOD.upper())

    def get_password_hash(self, password):
        return self.prefix + get_hash_base64(password, method=self.method)

    def validate_password_hash(self, password_hash_data, password):
        if not hasattr(self, "prefix"):
            return None
        if not password_hash_data.startswith(self.prefix):
            return None
        new_password_hash_data = self.get_password_hash(password)
        return new_password_hash_data == password_hash_data


def register_simple_password_hash(method, prefix, class_name_suffix=""):
    class_name = "".join(
        [x.title() for x in [method, "simple", "password", "hash", class_name_suffix]]
    )
    globals()[class_name] = create_new_class(
        class_name,
        (SimplePasswordHashBase,),
        {
            "method": method,
            "prefix": prefix,
        },
    )
    return globals()[class_name]


class SimpleSaltPasswordHashBase(PasswordHashMethodBase):
    method = DEFAULT_PASSWORD_HASH_METHOD
    prefix = "{{{method}}}".format(method=DEFAULT_PASSWORD_HASH_METHOD.upper())
    hash_size = 0
    salt_length = 8

    def get_hash_size(self):
        if self.hash_size == 0:
            gen_class = method_load(self.method)
            self.hash_size = gen_class().digest_size
        return self.hash_size

    def get_password_hash(self, password, salt_length=None, salt=None):
        if salt_length is None:
            salt_length = self.salt_length
        return self.prefix + get_salted_hash_base64(
            password, salt_length=salt_length, salt=salt, method=self.method
        )

    def validate_password_hash(self, password_hash_data, password):
        if not hasattr(self, "prefix"):
            return None
        if not password_hash_data.startswith(self.prefix):
            return None
        salt = base64utils.decodebytes(
            force_bytes(password_hash_data[len(self.prefix) :])
        )[self.get_hash_size() :]
        new_password_hash_data = self.get_password_hash(password, salt=salt)
        return new_password_hash_data == password_hash_data


def register_simple_salt_password_hash(
    method, prefix, hash_size=0, salt_length=8, class_name_suffix=""
):
    class_name = "".join(
        [
            x.title()
            for x in [method, "simple", "salt", "password", "hash", class_name_suffix]
        ]
    )
    globals()[class_name] = create_new_class(
        class_name,
        (SimpleSaltPasswordHashBase,),
        {
            "method": method,
            "prefix": prefix,
            "hash_size": hash_size,
            "salt_length": salt_length,
        },
    )
    return globals()[class_name]


class HexlifyPasswordHashBase(PasswordHashMethodBase):
    length = 40
    method = DEFAULT_HASH_METHOD

    def get_length(self):
        if self.length == 0:
            gen_class = method_load(self.method)
            self.length = 2 * gen_class().digest_size
        return self.length

    def get_password_hash(self, password):
        return get_hash_hexdigest(password, method=self.method)

    def validate_password_hash(self, password_hash_data, password):
        if not strutils.is_unhexlifiable(password_hash_data):
            return None
        if len(password_hash_data) != self.get_length():
            return None
        new_password_hash_data = self.get_password_hash(password)
        if new_password_hash_data == password_hash_data:
            return True
        else:
            return None


def register_hexlify_password_hash(method, length=0, class_name_suffix=""):
    class_name = "".join(
        [x.title() for x in [method, "hexlify", "password", "hash", class_name_suffix]]
    )
    globals()[class_name] = create_new_class(
        class_name,
        (HexlifyPasswordHashBase,),
        {
            "method": method,
            "length": length,
        },
    )
    return globals()[class_name]


# ##################################################################################
# HASH CALC METHOD ALIAS AREA
# ##################################################################################
get_file_hash = functools.partial(
    get_file_hash_result, result_encoder=HexlifyResultEncoder
)
get_file_hash_hexdigest = functools.partial(
    get_file_hash_result, result_encoder=HexlifyResultEncoder
)
get_file_hash_base64 = functools.partial(
    get_file_hash_result, result_encoder=Base64ResultEncoder
)
get_hash = functools.partial(
    get_hash_result,
    result_encoder=HexlifyResultEncoder,
)
get_hash_hexdigest = functools.partial(
    get_hash_result,
    result_encoder=HexlifyResultEncoder,
)
get_hash_digest = functools.partial(
    get_hash_result,
    result_encoder=DigestResultEncoder,
)
get_hash_base64 = functools.partial(
    get_hash_result,
    result_encoder=Base64ResultEncoder,
)

_not_simple_hash_algorithms = set(
    [
        "shake_128",
        "shake_256",
    ]
)
for _method in algorithms_available:
    if _method in _not_simple_hash_algorithms:
        continue
    # ##################################################################################
    # STRING HASH CALC METHOD ALIAS
    # ##################################################################################
    _name = "get_{method}_digest".format(method=_method)
    globals()[_name] = functools.partial(
        get_hash_result, method=_method, result_encoder=DigestResultEncoder
    )
    __all__.append(_name)

    _name = "get_{method}".format(method=_method)
    globals()[_name] = functools.partial(
        get_hash_result, method=_method, result_encoder=HexlifyResultEncoder
    )
    __all__.append(_name)

    _name = "get_{method}_hexdigest".format(method=_method)
    globals()[_name] = functools.partial(
        get_hash_result, method=_method, result_encoder=HexlifyResultEncoder
    )
    __all__.append(_name)

    _name = "get_{method}_base64".format(method=_method)
    globals()[_name] = functools.partial(
        get_hash_result, method=_method, result_encoder=Base64ResultEncoder
    )
    __all__.append(_name)

    # ##################################################################################
    # FILE HASH CALC METHOD ALIAS
    # ##################################################################################
    _name = "get_file_{method}_digest".format(method=_method)
    globals()[_name] = functools.partial(
        get_file_hash_result, method=_method, result_encoder=DigestResultEncoder
    )
    __all__.append(_name)

    _name = "get_file_{method}".format(method=_method)
    globals()[_name] = functools.partial(
        get_file_hash_result, method=_method, result_encoder=HexlifyResultEncoder
    )
    __all__.append(_name)

    _name = "get_file_{method}_hexdigest".format(method=_method)
    globals()[_name] = functools.partial(
        get_file_hash_result, method=_method, result_encoder=HexlifyResultEncoder
    )
    __all__.append(_name)

    _name = "get_file_{method}_base64".format(method=_method)
    globals()[_name] = functools.partial(
        get_file_hash_result, method=_method, result_encoder=Base64ResultEncoder
    )
    __all__.append(_name)

    # ##################################################################################
    # PBKDF2 METHOD ALIAS
    # ##################################################################################
    _name = "get_pbkdf2_{method}".format(method=_method)
    globals()[_name] = functools.partial(get_pbkdf2_hmac, hash_name=_method)
    __all__.append(_name)

    _name = "validate_pbkdf2_{method}".format(method=_method)
    globals()[_name] = validate_pbkdf2_hmac
    __all__.append(_name)

    password_hash_method_name = "PBKDF2_{method}".format(method=_method.upper())
    password_hash_method_class = register_pbkdf2_password_hash(
        _method, "pbkdf2_{method}$".format(method=_method), "_", class_name_suffix=""
    )
    register_password_hash_method(
        password_hash_method_name, password_hash_method_class()
    )
    __all__.append(password_hash_method_class.__name__)

    password_hash_method_name = "PBKDF2:{method}".format(method=_method.upper())
    password_hash_method_class = register_pbkdf2_password_hash(
        _method,
        "pbkdf2:{method}$".format(method=_method),
        ":",
        class_name_suffix="Colon",
    )
    register_password_hash_method(
        password_hash_method_name, password_hash_method_class()
    )
    __all__.append(password_hash_method_class.__name__)

    password_hash_method_name = "S{method}".format(method=_method.upper())
    password_hash_method_class = register_simple_salt_password_hash(
        _method, "{{S{method}}}".format(method=_method.upper()), class_name_suffix=""
    )
    register_password_hash_method(
        password_hash_method_name, password_hash_method_class()
    )
    __all__.append(password_hash_method_class.__name__)

    password_hash_method_name = "{method}".format(method=_method.upper())
    password_hash_method_class = register_simple_password_hash(
        _method, "{{{method}}}".format(method=_method.upper()), class_name_suffix=""
    )
    register_password_hash_method(
        password_hash_method_name, password_hash_method_class()
    )
    __all__.append(password_hash_method_class.__name__)

    password_hash_method_name = "{method}HEX".format(method=_method.upper())
    password_hash_method_class = register_hexlify_password_hash(
        _method, class_name_suffix=""
    )
    register_password_hash_method(
        password_hash_method_name, password_hash_method_class()
    )
    __all__.append(password_hash_method_class.__name__)
