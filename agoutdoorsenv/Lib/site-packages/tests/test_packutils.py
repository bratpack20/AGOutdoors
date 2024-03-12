#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *

import unittest
from zenutils import packutils
from zenutils import errorutils

class TestPackUtils(unittest.TestCase):

    def test01(self):
        pack = packutils.RcmPacker()
        package = pack.pack_result("hello")
        assert package["result"] == "hello"
        assert package["code"] == 0
        assert package["message"]

    def test02(self):
        error = Exception(123, "error message")
        pack = packutils.RcmPacker()
        package = pack.pack_error(error)
        assert package["result"] is None
        assert package["code"]
        assert package["message"]

    def test03(self):
        pack = packutils.RcmPacker()
        package = pack.pack_result("hello")
        assert pack.unpack(package) == "hello"

    def test04(self):
        error = Exception(123, "error message")
        pack = packutils.RcmPacker()
        package = pack.pack_error(error)
        with self.assertRaises(errorutils.BizErrorBase):
            pack.unpack(package)
