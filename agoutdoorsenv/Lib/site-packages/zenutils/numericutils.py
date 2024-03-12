#!/usr/bin/env python
# -*- coding: utf8 -*-
"""数值工具。"""
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
    "binary_decompose",
    "decimal_change_base",
    "get_float_part",
    "float_split",
    "infinity",
    "_infinity",
    "pinfinity",
    "ninfinity",
    "is_infinity",
    "from_bytes",
    "bytes2ints",
    "ints2bytes",
    "int2bytes",
]


def binary_decompose(value):
    values = set()
    binary_string = bin(value)[2:]
    length = len(binary_string) - 1
    for c in binary_string:
        if c == "1":
            values.add(2**length)
        length -= 1
    return values


def decimal_change_base(
    number, base=16, characters="0123456789abcdefghijklmnopqrstuvwxyz"
):
    digits = []
    while number:
        digits.append(number % base)
        number //= base
    digits.reverse()
    if not digits:
        digits.append(0)
    if characters:
        return "".join([characters[x] for x in digits])
    else:
        return digits


def get_float_part(value, precision=7):
    value = abs(value)
    mod = 10**precision
    value_all = int(value * mod)
    value_int = int(value) * mod
    value_float = value_all - value_int
    return value_float


def float_split(value, precision=7):
    if value >= 0:
        sign = 1
    else:
        sign = -1
    value = abs(value)
    int_value = int(value)
    float_value = get_float_part(value, precision)
    return sign, int_value, float_value


infinity = float("inf")  # Positive infinity
_infinity = float("-inf")  # Negative infinity

pinfinity = infinity
ninfinity = _infinity


def is_infinity(value):
    """Check if the value is infinity value or not.

    @Returns:
        (bool): True means the value is infinity. False means the value is NOT infinity.

    @Parameters:
        value(float): The value to be checked.
    """
    if type(value) == float and (
        str(value) in ["inf", "-inf"] or value in [infinity, _infinity]
    ):
        return True
    else:
        return False


def from_bytes(data, byteorder="big", signed=False):
    """int.from_bytes entrypoint."""
    if hasattr(int, "from_bytes"):
        return int.from_bytes(data, byteorder, signed=signed)
    else:
        return _from_bytes(data, byteorder, signed=signed)


def _from_bytes(data, byteorder="big", signed=False):
    """int.from_bytes backport."""
    # int.from_bytes(...) for python2.7
    import struct
    from zenutils import strutils

    # length == 0
    if not data:
        return 0

    # length == 1
    if len(data) < 2:
        if signed:
            formatter = "b"
        else:
            formatter = "B"
        return struct.unpack(formatter, data)[0]

    # length >= 2
    if byteorder != "big":
        data = strutils.reverse(data)

    if len(data) % 2 != 0:
        last_delta = 2**8
    else:
        last_delta = 2**16

    result = 0
    delta = 2**16
    data = strutils.chunk(data, 2)
    for idx in range(len(data)):
        if len(data[idx]) != 2:
            data[idx] = b"\x00" + data[idx]

    formatter = ">H"
    if not signed:
        result = struct.unpack(formatter, data[0])[0]
    else:
        result = struct.unpack(formatter.lower(), data[0])[0]
    for idx, chunk in enumerate(data[1:]):
        if idx == len(data[1:]) - 1:
            delta = last_delta
        result = result * delta + struct.unpack(formatter, chunk)[0]
    return result


def bytes2ints(data):
    """Turn bytes to int arrary.

    @Returns:
        (list of int): int array.

    @Parameters:
        data(bytes): The bytes data.

    @Examples:
        assert strutils.bytes2ints(b'hello') == [104, 101, 108, 108, 111]
    """
    if PY2:
        return [ord(x) for x in data]
    else:
        return list(data)


def ints2bytes(ints):
    return b"".join([int2bytes(x) for x in ints])


def int2bytes(value, length=0, byteorder="big", signed=False):
    """int.to_bytes. Auto detect the samllest length."""
    if length == 0:
        if signed:
            c = -128
            length = 1
            while c > value:
                c *= 256
                length += 1
        else:
            c = 1
            while c <= value:
                c *= 256
                length += 1
    if hasattr(int, "to_bytes"):
        result = value.to_bytes(length, byteorder, signed=signed)
        if result == b"":
            if signed:
                result = b"\xff"
            else:
                result = b"\x00"
        return result
    else:
        return _int2bytes(value, length, byteorder, signed=signed)


def _int2bytes(value, length=0, byteorder="big", signed=False):
    """int.to_bytes"""
    if length == 0:
        if signed:
            c = -128
            length = 1
            while c > value:
                c *= 256
                length += 1
        else:
            c = 1
            while c <= value:
                c *= 256
                length += 1
    bs = []
    if value >= 0:
        while value:
            bs.append(value % 256)
            value = value // 256
    else:
        while value != -1:
            bs.append(value % 256)
            value = value // 256
    if signed:
        pad = 255
    else:
        pad = 0
    if length:
        bs += [pad] * (length - len(bs))
    if not bs:
        bs.append(pad)
    if byteorder == "big":
        bs.reverse()
    result = b"".join([bchar(x) for x in bs])
    return result
