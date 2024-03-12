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
from zenutils.sixutils import *

import unittest
from zenutils import baseutils


class TestBaseUtils(unittest.TestCase):
    def test01(self):
        assert not baseutils.Null is None
        assert baseutils.Null is baseutils.Null
        a = baseutils.Null
        b = baseutils.Null
        assert a is b
        assert a == b
