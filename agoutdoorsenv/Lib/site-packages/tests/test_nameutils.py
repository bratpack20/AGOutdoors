#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *

import unittest
from zenutils import nameutils

class TestNameUtils(unittest.TestCase):

    def test01(self):
        name = nameutils.get_random_name()
        assert 2 <= len(name) <= 4

    def test02(self):
        assert nameutils.guess_surname("黄某某") == "黄"
        assert nameutils.guess_surname("张某某") == "张"
        assert nameutils.guess_surname("John Smith") == "Smith"
        assert nameutils.guess_surname("Tom") == "Tom"
        assert nameutils.guess_surname("西门吹雪") == "西门"
        assert nameutils.guess_surname("申屠雪") == "申屠"
        assert nameutils.guess_surname("司空寻") == "司空"
        assert nameutils.guess_surname("轩辕羿") == "轩辕"
        assert nameutils.guess_surname("欧阳修") == "欧阳"
