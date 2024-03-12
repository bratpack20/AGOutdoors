#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *

import unittest
from zenutils import serviceutils

class TestServiceUtils(unittest.TestCase):

    def test01(self):
        service = serviceutils.DebugService()
        assert service.ping() == "pong"
    
    def test02(self):
        config = {}
        service = serviceutils.DebugService(config)
        assert service.echo("hello world") == "hello world"

    def test03(self):
        service = serviceutils.DebugService()
        methods = service.get_methods()
        assert methods
        assert isinstance(methods, list)
        assert "debug.ping" in dict(methods)

    def test04(self):
        service = serviceutils.DebugService(namespace="test")
        methods = service.get_methods()
        assert methods
        assert isinstance(methods, list)
        assert "test.ping" in dict(methods)

    def test05(self):
        service = serviceutils.DebugService(namespace="")
        methods = service.get_methods()
        assert methods
        assert isinstance(methods, list)
        assert "ping" in dict(methods)

    def test06(self):
        service = serviceutils.DebugService()
        assert service.get_ignore_methods()
    
    def test07(self):
        service = serviceutils.DebugService()
        assert service.get_namespace() == "debug"
    
    def test08(self):
        service = serviceutils.DebugService(namespace="test")
        assert service.get_namespace() == "test"

    def test09(self):
        service = serviceutils.DebugService(namespace="")
        assert service.get_namespace() == ""

    