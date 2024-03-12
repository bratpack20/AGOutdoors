#!/usr/bin/env python
# -*- coding: utf8 -*-
"""能用基础工具。"""
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
    "Null",
]


class _Null(object):
    """Custom Null value."""


Null = _Null()
