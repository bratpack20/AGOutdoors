#!/usr/bin/env python
# -*- coding: utf8 -*-
"""PYTHON2/3兼容性处理工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

__all__ = [
    "PY2",
    "PY3",
    "STR_TYPE",
    "BYTES_TYPE",
    "BASESTRING_TYPES",
    "TEXT",
    "BYTES",
    "INT_TO_BYTES",
    "force_bytes",
    "force_text",
    "bytes_to_array",
    "bstr_to_array",
    "bchar",
    "default_encodings",
    "default_encoding",
    "NUMERIC_TYPES",
    "create_new_class",
]

import sys

default_encodings = ["utf-8", "gb18030"]
default_encoding = "utf-8"

INT_TO_BYTES = {}
if sys.version_info.major == 2:
    range = xrange
    __all__.append("range")
    PY2 = True
    PY3 = False
    BASESTRING_TYPES = (basestring, str, unicode)
    STR_TYPE = unicode
    BYTES_TYPE = str
    for i in range(256):
        INT_TO_BYTES[i] = chr(i)
    NUMERIC_TYPES = (int, long, float)

    def create_new_class(name, bases, dict, **kwargs):
        if isinstance(name, unicode):
            name = name.encode("utf-8")
        return type(name, bases, dict, **kwargs)

else:
    PY2 = False
    PY3 = True
    BASESTRING_TYPES = (str, bytes)
    STR_TYPE = str
    BYTES_TYPE = bytes
    for i in range(256):
        INT_TO_BYTES[i] = bytes([i])
    NUMERIC_TYPES = (int, float)
    create_new_class = type
    unicode = str
    __all__.append("unicode")

if sys.version_info.major == 2:
    Interrupted = InterruptedError = KeyboardInterrupt
    __all__.append("InterruptedError")
elif sys.version_info.major == 3:
    if sys.version_info.minor in [0, 1, 2]:
        Interrupted = InterruptedError = KeyboardInterrupt
        __all__.append("InterruptedError")
    else:
        Interrupted = InterruptedError
else:
    Interrupted = InterruptedError


def force_bytes(value, encoding=None):
    """Turn all things to bytes. If the original value is bytes, try to decode with encoding given or default encodings utf-8 and gb18030.

    @Returns:
        (str): Returns a str value.

    @Parameters:
        value(str or bytes or any): The value to be transformed.
        encoding(str or list[str], optional): The encoding method will be used to decode.

    @Example:
        assert sixutils.force_bytes(b'hello') == b'hello'
        assert sixutils.force_bytes('测试'.encode('utf-8')) == '测试'
        assert sixutils.force_bytes('hello') == b'hello'
        assert sixutils.force_bytes(1234) == b'1234'
        assert sixutils.force_bytes([1,2,3]) == b"[1, 2, 3]"
    """
    if callable(value):
        value = value()
    if value is None:
        return None
    if isinstance(value, BYTES_TYPE):
        return value
    encoding = encoding or default_encoding
    if isinstance(value, STR_TYPE):
        return value.encode(encoding)
    else:
        value = STR_TYPE(value)
        return value.encode(encoding)


def force_text(value, encoding=None):
    """Turn all things to text. If the original value is bytes, try to decode with encoding given or default encodings utf-8 and gb18030.

    @Returns:
        (str): Returns a str value.

    @Parameters:
        value(str or bytes or any): The value to be transformed.
        encoding(str or list[str], optional): The encoding method will be used to decode.

    @Example:
        assert sixutils.force_text(b'hello') == 'hello'
        assert sixutils.force_text('测试'.encode('utf-8')) == '测试'
        assert sixutils.force_text('hello') == 'hello'
        assert sixutils.force_text(1234) == '1234'
        assert sixutils.force_text([1,2,3]) == "[1, 2, 3]"
    """
    if callable(value):
        value = value()
    if value is None:
        return None
    if isinstance(value, STR_TYPE):
        return value
    if not isinstance(value, BYTES_TYPE):
        return STR_TYPE(value)
    if not encoding:
        encodings = default_encodings
    elif isinstance(encoding, (set, list, tuple)):
        encodings = encoding
    else:
        encodings = [encoding]
    last_error = None
    for encoding in encodings:
        try:
            return value.decode(encoding)
        except UnicodeDecodeError as error:
            last_error = error
    if last_error:
        last_error.encoding = " or ".join(encodings)
        raise last_error


def bytes_to_array(data):
    """Turn bytes into list of bytes char.

    @Returns:
        (list of bytes char): Returns the list of the bytes char.

    @Parameters:
        data(str or bytes): The data to be splitted.

    @Example:
        sixutils.bytes_to_array(b"hello") == [b"h", b"e", b"l", b"l", b"o"]
    """
    data = force_bytes(data)
    if PY2:
        return list(data)
    else:
        return [data[idx : idx + 1] for idx in range(len(data))]


def bstr_to_array(data):
    """Get char array of the given data.

    Returns:
        (list of char): The char array of the given daa.

    @Parameters:
        data(str or bytes): The data will be split into chars.

    @Examples:
        assert sixutils.bstr_to_array("hello") == ["h", "e", "l", "l", "o"]
        assert sixutils.bstr_to_array(b"hello") == [b"h", b"e", b"l", b"l", b"o"]
    """
    if isinstance(data, BYTES_TYPE):
        return bytes_to_array(data)
    else:
        return list(data)


def bchar(value):
    """Similar as chr(value) by returns bytes char. The value is in [0, 255].

    @Returns:
        (bytes char): One length bytes.

    @Parameters:
        value(int): The int value between [0, 255].

    @Example:
        assert bchar(0) == b'\\x00';
        assert bchar(1) == b'\\x01';
        assert bchar(255) == b'\\xff'.
    """
    return INT_TO_BYTES[value]


def TEXT(value):
    """Alias for force_text."""
    return force_text(value)


def BYTES(value):
    """Alias for force_bytes."""
    return force_bytes(value)
