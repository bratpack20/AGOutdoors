#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *


import os
import uuid
import unittest
from zenutils import httputils

class TestHttpUtils(unittest.TestCase):

    def test01(self):
        info = httputils.get_urlinfo("https://127.0.0.1:8080/tmp/?ts=1234")
        assert info.netloc == "127.0.0.1:8080"
        assert info.scheme == "https"
        assert info.path == "/tmp/"
        assert info.query == "ts=1234"

    def test02(self):
        filename1 = httputils.get_url_filename("http://a.b.com/")
        filename2 = httputils.get_url_filename("http://a.b.com/a.txt")
        filename3 = httputils.get_url_filename("http://a.b.com/hello")
        filename4 = httputils.get_url_filename("http://a.b.com/hello/")
        assert filename1 == "index.html"
        assert filename2 == "a.txt"
        assert filename3 == "hello"
        assert filename4 == "index.html"

    def test03(self):
        filename1 = httputils.get_url_save_path("http://a.b.com/", "tmp")
        filename2 = httputils.get_url_save_path("http://a.b.com/a.txt", "tmp")
        filename3 = httputils.get_url_save_path("http://a.b.com/hello", "tmp")
        filename4 = httputils.get_url_save_path("http://a.b.com/hello/", "tmp")
        assert filename1 == os.path.abspath("tmp/index.html")
        assert filename2 == os.path.abspath("tmp/a.txt")
        assert filename3 == os.path.abspath("tmp/hello")
        assert filename4 == os.path.abspath("tmp/index.html")

    def test04(self):
        name1 = httputils.get_sitename("http://a.b.com")
        name2 = httputils.get_sitename("http://127.0.0.1")
        name3 = httputils.get_sitename("http://a.b.com:8443")
        name4 = httputils.get_sitename("http://127.0.0.1:8443")
        name5 = httputils.get_sitename("http://a.b.com/hello/")
        name6 = httputils.get_sitename("http://127.0.0.1/a.txt")
        name7 = httputils.get_sitename("http://a.b.com:8443/world")
        name8 = httputils.get_sitename("http://127.0.0.1:8443/test/b.txt")
        assert name1 == "a.b.com"
        assert name2 == "127.0.0.1"
        assert name3 == "a.b.com"
        assert name4 == "127.0.0.1"
        assert name5 == "a.b.com"
        assert name6 == "127.0.0.1"
        assert name7 == "a.b.com"
        assert name8 == "127.0.0.1"

    def test05(self):
        filename = str(uuid.uuid4())
        for url in ["http://www.baidu.com", "https://www.baidu.com"]:
            try:
                size = httputils.download(url, filename)
                stats = os.stat(filename)
                assert size == stats.st_size
            finally:
                if os.path.exists(filename):
                    os.unlink(filename)
