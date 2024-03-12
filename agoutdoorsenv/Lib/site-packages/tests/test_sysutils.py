#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *

import time
import threading
import unittest

from zenutils import sysutils


def fakeproc():
    print("i am in fake process...")

class TestSysUtils(unittest.TestCase):

    def test01(self):
        w1 = sysutils.get_worker_id()
        w2 = sysutils.get_worker_id()
        assert w1 == w2
    
    def test02(self):
        # thread id may reused after a thread terminated
        info = {}
        set_lock = threading.Lock()
        def get_info(info, name):
            with set_lock:
                info[name] = sysutils.get_worker_id()
            time.sleep(5)
        get_info(info, "w0")
        t1 = threading.Thread(target=get_info, args=[info, "w1"])
        t2 = threading.Thread(target=get_info, args=[info, "w2"])
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        assert info["w0"] != info["w1"]
        assert info["w1"] != info["w2"]
        assert info["w2"] != info["w0"]

    def test03(self):
        w1 = sysutils.get_worker_id("redis")
        w2 = sysutils.get_worker_id("mysql")
        assert w1 != w2


    def test04(self):
        code, stdout, stderr = sysutils.execute_script("hostname")
        assert code == 0
        assert stdout != ""
        assert stderr == ""
        assert isinstance(stdout, STR_TYPE)
        assert isinstance(stderr, STR_TYPE)

    def test05(self):
        filename1 = sysutils.get_random_script_name(suffix=".sh")
        assert filename1.endswith(".sh")

        filename2 = sysutils.get_random_script_name(suffix=".py")
        assert filename2.endswith(".py")

        filename3 = sysutils.get_random_script_name()
        filename4 = sysutils.get_random_script_name()
        assert filename3 != filename4

    def test06(self):
        ip1 = sysutils.get_node_ip()
        ip2 = sysutils.get_node_ip()
        assert ip1
        assert ip1 == ip2
