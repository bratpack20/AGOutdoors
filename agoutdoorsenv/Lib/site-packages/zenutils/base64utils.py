#!/usr/bin/env python
# -*- coding: utf8 -*-
"""BASE64相关工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

import base64

__all__ = [] + base64.__all__

# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
from base64 import *

_globals = globals()

if ("encodebytes" not in _globals) and ("encodestring" in _globals):
    _globals["encodebytes"] = _globals["encodestring"]
    __all__.append("encodebytes")

if ("decodebytes" not in _globals) and ("decodestring" in _globals):
    _globals["decodebytes"] = _globals["decodestring"]
    __all__.append("decodebytes")
