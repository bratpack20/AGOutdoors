#!/usr/bin/env python
# -*- coding: utf8 -*-
"""JSON工具。"""
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
    "register_global_encoder",
    "make_simple_json_encoder",
    "SimpleJsonEncoder",
    "simple_json_dumps",
]

import json
import json.encoder
import uuid
import binascii
import datetime
import decimal
from io import BytesIO
from functools import partial

from .sixutils import BASESTRING_TYPES
from .sixutils import PY2
from .sixutils import force_text
from .sixutils import BYTES_TYPE
from . import base64utils
from . import funcutils
from . import strutils

DefaultSimpleJsonEncoderBase = json.encoder.JSONEncoder
DEFAULT_ERROR_CODE = 1


class JsonEncodeLibrary(object):
    """JSON序列化库。"""

    def __init__(self, base_class=DefaultSimpleJsonEncoderBase):
        self.base_class = base_class
        self.encoders = {}
        self._encoder = None

    def get_encoder(self):
        """获取编码器。"""
        if self._encoder is not None:
            return self._encoder

        this = self

        class SimpleJsonEncoderBase(this.base_class):
            """根据base_class编码器，派生自定义编码器。"""

            def default(self, o):
                for type_class, encoder in this.encoders.items():
                    try:
                        isinstance_flag = isinstance(o, type_class)
                    except:  # pylint: disable=bare-except
                        isinstance_flag = False
                    if isinstance_flag:
                        return encoder(o)
                    try:
                        issubclass_flag = issubclass(o, type_class)
                    except:  # pylint: disable=bare-except
                        issubclass_flag = False
                    if issubclass_flag:
                        return encoder(o)
                # pylint: disable=bad-super-call
                return super(SimpleJsonEncoder, self).default(o)

        if PY2:
            _default_encode_basestring = json.encoder.encode_basestring
            _default_encode_basestring_ascii = json.encoder.encode_basestring_ascii

            def _encode_basestring(s):
                try:
                    s = force_text(s)
                except:  # pylint: disable=bare-except
                    s = encode_bytes(s)
                return _default_encode_basestring(s)

            def _encode_basestring_ascii(s):
                try:
                    s = force_text(s)
                except:  # pylint: disable=bare-except
                    s = encode_bytes(s)
                return _default_encode_basestring_ascii(s)

            # pylint: disable=redefined-outer-name
            class SimpleJsonEncoder(SimpleJsonEncoderBase):
                """自定义的编码器。"""

                def encode(self, o):
                    json.encoder.encode_basestring = _encode_basestring
                    json.encoder.encode_basestring_ascii = _encode_basestring_ascii
                    result = super(SimpleJsonEncoder, self).encode(o)
                    json.encoder.encode_basestring = _default_encode_basestring
                    json.encoder.encode_basestring_ascii = (
                        _default_encode_basestring_ascii
                    )
                    return result

        else:

            class SimpleJsonEncoder(SimpleJsonEncoderBase):
                """自定义的编码器。"""

        self._encoder = SimpleJsonEncoder
        setattr(self._encoder, "library", this)
        return self._encoder

    def register(self, type_class, encoder):
        """注册编码器。"""
        self.encoders[type_class] = encoder

    def unregister(self, type_class):
        """删除编码器。"""
        if type_class in self.encoders:
            del self.encoders[type_class]


DATETIME_ISO_FORMAT = "isoformat"
DATETIME_FORMAT = DATETIME_ISO_FORMAT


def set_datetime_format(format=DATETIME_ISO_FORMAT):
    """设置全局datetime序列化格式。"""
    # pylint: disable=redefined-builtin
    # pylint: disable=global-statement
    global DATETIME_FORMAT
    DATETIME_FORMAT = format


def encode_datetime(value):
    """日期数据序列化。"""
    if DATETIME_FORMAT == DATETIME_ISO_FORMAT:
        return value.isoformat()
    else:
        return value.strftime(DATETIME_FORMAT)


def encode_bytes(value):
    """字节流数据序列化。"""
    return binascii.hexlify(value).decode()


def encode_basestring(value):
    """
    @todo: 不明白做什么的。
    """
    if isinstance(value, BYTES_TYPE):
        return encode_bytes(value)
    else:
        return value


def encode_decimal(value):
    """decimal类型编码。

    @todo: 转化为float类型安全吗？还不如转化为string类型呢。
    """
    return float(value)


def encode_complex(value):
    """complex类型编码。"""
    return [value.real, value.imag]


def encode_uuid(value):
    """UUID类型编码。"""
    return str(value)


def encode_image(image):
    """PIL Image类型编码。"""
    buffer = BytesIO()
    image.save(buffer, format="png")
    # pylint: disable=consider-using-f-string
    return """data:image/{format};base64,{data}""".format(
        format=format,
        data=force_text(base64utils.encodebytes(buffer.getvalue())),
    )


def encode_exception(error):
    """Exception实例编码。"""
    if error.args:
        try:
            code = strutils.force_int(error.args[0])
            message = " ".join(error.args[1:])
            return {
                "code": code,
                "message": message,
            }
        except:  # pylint: disable=bare-except
            message = " ".join(error.args)
            if message:
                return {"code": DEFAULT_ERROR_CODE, "message": message}
    return {
        "code": DEFAULT_ERROR_CODE,
        "message": funcutils.get_class_name(error),
    }


def encode_bizerror(error):
    """BizError实例编码。"""
    return error.json


def encode_django_model(django_model):
    """Django数据模型实例编码。"""
    # pylint: disable=import-outside-toplevel
    # 避免zenutils项目对django的依赖。
    # 如果你需要序列化Django数据模型，则你需要django这个依赖，可以在你的底层项目中添加django依赖。
    from django.core import serializers

    try:
        isinstance_flag = isinstance(django_model, Model)
    except:  # pylint: disable=bare-except
        isinstance_flag = False
    try:
        issubclass_flag = issubclass(django_model, Model)
    except:  # pylint: disable=bare-except
        issubclass_flag = False
    if issubclass_flag:
        # pylint: disable=protected-access
        return ".".join([django_model._meta.app_label, django_model._meta.model_name])
    if isinstance_flag:
        # pylint: disable=protected-access
        pk_name = django_model._meta.pk.name
        text = serializers.serialize("json", [django_model])
        results = json.loads(text)
        obj = results[0]["fields"]
        obj[pk_name] = results[0]["pk"]
        return obj
    return None


def encode_django_queryset(django_queryset):
    """Django数据模型查询结果集的编码。"""
    # pylint: disable=import-outside-toplevel
    from django.core import serializers

    # pylint: disable=protected-access
    pk_name = django_queryset.model._meta.pk.name
    text = serializers.serialize("json", django_queryset)
    results = json.loads(text)
    data = []
    for result in results:
        obj = result["fields"]
        obj[pk_name] = result["pk"]
        data.append(obj)
    return data


def encode_django_query(django_query):
    """Django数据模型查询的编码。"""
    return str(django_query)


GLOBAL_ENCODERS = {}


def register_global_encoder(type_class, encoder):
    """Register a new encoder type to the global-encoder-collections.

    @Returns:
        (None): Nothing.

    @Paramters:
        type_class(Any type): The type has a custom encode callback.
        encoder(Callable): A callable object that
                            takes one parameter which is to be json serialized
                            and returns the system serializable value.


    @Example:
        class Model(object):
            def __init__(self):
                self.name = ""
                self.age = 0

            def json(self):
                return {
                    "name": self.name,
                    "age": self.age,
                }

        def model_encoder(o):
            return o.json()

        register_global_encoder(Model, model_encoder)
    """
    type_classes = []
    if isinstance(type_class, (list, tuple, set)):
        type_classes = type_class
    else:
        type_classes = [type_class]
    for type_class in type_classes:
        GLOBAL_ENCODERS[type_class] = encoder


def register_simple_encoders(library):
    """Copy the encoders in the global-encoder-collections to a new encoder library instance.

    @Returns:
        (None): Nothing.

    @Parameters:
        library(JsonEncodeLibrary): An instance of JsonEncodeLibrary.
    """
    for type_class, encoder in GLOBAL_ENCODERS.items():
        library.register(type_class, encoder)


register_global_encoder(
    (datetime.datetime, datetime.date, datetime.time), encode_datetime
)
register_global_encoder(decimal.Decimal, encode_decimal)
register_global_encoder(complex, encode_complex)
register_global_encoder(uuid.UUID, encode_uuid)
register_global_encoder(BASESTRING_TYPES, encode_basestring)


try:
    from zenutils import dictutils

    register_global_encoder(dictutils.HttpHeadersDict, lambda x: x.data)
except Exception:  # pylint: disable=broad-exception-caught
    pass

try:
    from zenutils import funcutils

    for exception_class in funcutils.get_all_builtin_exceptions():
        register_global_encoder(exception_class, encode_exception)
except Exception:  # pylint: disable=broad-exception-caught
    pass

try:
    from PIL.Image import Image

    register_global_encoder(Image, encode_image)
except ImportError:
    pass

try:
    from django.db.models import Model

    register_global_encoder(Model, encode_django_model)
except ImportError:
    pass

try:
    from bizerror import BizErrorBase

    register_global_encoder(BizErrorBase, encode_bizerror)
except ImportError:
    pass

try:
    from django.db.models import QuerySet

    register_global_encoder(QuerySet, encode_django_queryset)
except ImportError:
    pass

try:
    from django.db.models.sql.query import Query

    register_global_encoder(Query, encode_django_query)
except ImportError:
    pass


def make_simple_json_encoder(base_class=DefaultSimpleJsonEncoderBase):
    """创建默认json编码器。"""
    library = JsonEncodeLibrary(base_class)
    register_simple_encoders(library)
    return library.get_encoder()


SimpleJsonEncoder = make_simple_json_encoder()

# 最终用户使用的方法
# 使用方法同json.dumps()
simple_json_dumps = partial(json.dumps, cls=SimpleJsonEncoder)
