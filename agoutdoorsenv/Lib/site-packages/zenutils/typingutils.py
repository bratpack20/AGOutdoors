#!/usr/bin/env python
# -*- coding: utf8 -*-
"""类型转化工具。"""
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
    "STRING_ENCODINGS",
    "register_global_caster",
    "smart_cast",
    "Number",
]

import json
import binascii
import uuid
from numbers import Number

STRING_ENCODINGS = ["utf-8", "gb18030"]


def cast_int(value):
    """Change the value to int value.

    @Returns:
        (None or int): Try to change the value to int.
                       If value is None or empty string, returns None value.

    @Parameters:
        value(Any): Any value that will be changed to int value.

    @Raises:
        ValueError: invalid literal for int() with base 10: 'xxx'
        TypeError: int() argument must be a string, a bytes-like object or a number, not 'XxxType'
    """
    if value is None:
        return None
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        if not value.strip():
            return None
    if isinstance(value, int):
        return value
    return int(value)


def cast_float(value):
    """Change the value to float value.

    @Returns:
        (None or float): Try to change the value to float.
                         If value is None or empty string, returns None value.

    @Parameters:
        value(Any): Any value that will be changed to float value.

    @Raises:
        ValueError: could not convert string to float: 'xxx'
        TypeError: float() argument must be a string or a number, not 'XxxType'
    """
    if value is None:
        return None
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        if not value.strip():
            return None
    if isinstance(value, float):
        return value
    return float(value)


def cast_bool(value):
    """Change the value to bool value.

    @Returns:
        (None or bool): Try to change the value to bool.
                        If value is None or empty string, returns None value.

    @Parameters:
        value(Any): Any value that will be changed to float value.
    """
    if value is None:
        return None
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        if not value.strip():
            return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        if value.lower() in [
            "true",
            "yes",
            "y",
            "t",
            "1",
            "on",
            "active",
            "ok",
            b"true",
            b"yes",
            b"y",
            b"t",
            b"1",
            b"on",
            b"active",
            b"ok",
        ]:
            return True
        else:
            return False
    if value:
        return True
    else:
        return False


def cast_list(value):
    from zenutils.strutils import force_type_to

    if value is None:
        return None
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        if not value.strip():
            return None
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        try:
            value = json.loads(value)
        except:
            try:
                value = [x.strip() for x in value.split(force_type_to(",", value))]
            except:
                pass
    if not isinstance(value, list):
        return [value]
    else:
        return value


def cast_bytes(value):
    from zenutils import strutils
    from zenutils import base64utils

    if value is None:
        return None
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        if not value.strip():
            return None
    if isinstance(value, BYTES_TYPE):
        return value
    if isinstance(value, STR_TYPE):
        if strutils.is_unhexlifiable(value):
            value = force_bytes(value)
            return binascii.unhexlify(value)
        elif strutils.is_base64_decodable(value):
            value = force_bytes(value)
            return base64utils.decodebytes(value)
        elif strutils.is_urlsafeb64_decodable(value):
            value = force_bytes(value)
            return base64utils.urlsafe_b64decode(value)
    return force_bytes(value)


def cast_str(value):
    if value is None:
        return None
    if isinstance(value, STR_TYPE):
        return value
    return force_text(value)


def cast_dict(value):
    if value is None:
        return None
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        if not value.strip():
            return None
    if isinstance(value, dict):
        return value
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        try:
            return json.loads(value)
        except:
            pass
    return dict(value)


def cast_numeric(value):
    if value is None:
        return None
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        if not value.strip():
            return None
    if isinstance(value, Number):
        return value
    value = force_text(value)
    if "." in value:
        return float(value)
    else:
        return int(value)


def cast_uuid(value):
    """Change the value to UUID type.

    @Returns:
        (UUID): The UUID typed value.

    @Parameters:
        value(Any): Any value that can be changed to UUID type.

    @Examples:
        assert str(cast_uuid(85188153587611980436344659581497329339)) == "4016a43f-406e-47b4-b332-e0f9016546bb"
        assert str(cast_uuid("4016a43f-406e-47b4-b332-e0f9016546bb")) == "4016a43f-406e-47b4-b332-e0f9016546bb"
        assert str(cast_uuid((1075225663, 16494, 18356, 179, 50, 247360074892987))) == "4016a43f-406e-47b4-b332-e0f9016546bb"
        assert str(cast_uuid(b'@\x16\xa4?@nG\xb4\xb32\xe0\xf9\x01eF\xbb')) == "4016a43f-406e-47b4-b332-e0f9016546bb"
    """
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(bytes=value)
    except:
        pass
    try:
        return uuid.UUID(fields=value)
    except:
        pass
    try:
        return uuid.UUID(int=value)
    except:
        pass
    return uuid.UUID(value)


TYPE_CASTERS = {}


def register_global_caster(type, caster):
    TYPE_CASTERS[type] = caster


register_global_caster(int, cast_int)
register_global_caster(float, cast_float)
register_global_caster(bool, cast_bool)
register_global_caster(BYTES_TYPE, cast_bytes)
register_global_caster(STR_TYPE, cast_str)
register_global_caster(list, cast_list)
register_global_caster(dict, cast_dict)
register_global_caster(Number, cast_numeric)
register_global_caster(uuid.UUID, cast_uuid)

try:
    import typing

    register_global_caster(typing.List, cast_list)
    register_global_caster(typing.Mapping, cast_dict)
except Exception:
    pass


def smart_cast(type, value, field_name=None):
    """Cast the value to the given type smartly.

    @Returns:
        (Any): The given typed value.

    @Parameters:
        type(Class): The type you want the value changed to.
        value(Any): The value will be changed.
        field_name(str, optional):  It is used in the message of the exception
                                    which will be raised if the value failed to change into the given type.

    @Examples:
        assert smart_cast(int, "1234") == 1234
        assert smart_cast(bool, "yes") is True
        assert smart_cast(str, b"hello") == "hello"
    """
    if type in TYPE_CASTERS:
        type_func = TYPE_CASTERS[type]
    elif callable(type):
        type_func = type
    else:
        if field_name:
            raise TypeError(
                "not supported type, field={field_name}, type={type}, value={value}".format(
                    field_name=field_name,
                    type=force_text(type(value)),
                    value=force_text(value),
                )
            )
        else:
            raise TypeError(
                "not supported type, type={type}, value={value}".format(
                    type=force_text(type(value)),
                    value=force_text(value),
                )
            )
    return type_func(value)
