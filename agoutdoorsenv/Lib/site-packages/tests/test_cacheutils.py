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

import random
import unittest
from zenutils import cacheutils

TEST_CACHEUTILS_COUNTER = 0


class Object(object):
    """临时简易类，用于生成cache holder。"""


class TestCacheUtils(unittest.TestCase):
    """缓存单元测试用例。"""

    def test01(self):
        """测试get_cached_value常规使用的测试。"""
        holder = Object()

        def say_hi1():
            return "hi"

        assert cacheutils.get_cached_value(holder, "say_hi1", say_hi1) == "hi"

    def test02(self):
        """通过全局计数器测试get_cached_value的有效性。"""
        global TEST_CACHEUTILS_COUNTER  # pylint: disable=global-statement
        TEST_CACHEUTILS_COUNTER = 0
        holder = Object()

        def counter():
            global TEST_CACHEUTILS_COUNTER  # pylint: disable=global-statement
            TEST_CACHEUTILS_COUNTER += 1
            return TEST_CACHEUTILS_COUNTER

        assert cacheutils.get_cached_value(holder, "counter", counter) == 1
        assert cacheutils.get_cached_value(holder, "counter", counter) == 1

    def test03(self):
        """当指定了holder和key时。直接调用函数即可缓存。"""
        holder = Object()

        @cacheutils.cache(holder, "_num")
        def get_number3():
            return random.randint(1, 10)

        value1 = get_number3()
        value2 = get_number3()
        value3 = get_number3()
        assert value1
        assert value1 == value2 == value3

    def test04(self):
        """当指定的holder为None时，相当于没有指定holder。需要在调用参数中指定holder。"""

        @cacheutils.cache(None, "_num")
        def get_number4():
            """每次实际调用，将生成新的随机数。"""
            return random.randint(1, 10)

        holder = Object()
        value1 = get_number4(holder)  # pylint: disable=too-many-function-args
        value2 = get_number4(holder)  # pylint: disable=too-many-function-args
        value3 = get_number4(holder)  # pylint: disable=too-many-function-args
        assert value1
        assert value1 == value2 == value3

    def test5(self):
        """cache测试。

        当没有指定缓存holder及key时，调用时的前两个参数分别是缓存holder和key。
        """

        @cacheutils.cache()
        def get_number5():
            """每次实际调用，将生成新的随机数。"""
            return random.randint(1, 10)

        holder = Object()
        value1 = get_number5(holder, "_num")  # pylint: disable=too-many-function-args
        value2 = get_number5(holder, "_num")  # pylint: disable=too-many-function-args
        value3 = get_number5(holder, "_num")  # pylint: disable=too-many-function-args
        assert value1
        assert value1 == value2 == value3

    def test6(self):
        """ReqIdCache重复性检验的测试。"""
        cachedb = cacheutils.ReqIdCache(10)
        assert cachedb.exists(1) is False
        assert cachedb.exists("2") is False
        # 插入1后
        cachedb.add("1")
        # 判断1存在
        assert cachedb.exists("1")
        # 插入1000个值，将已插入的1溢出
        for inum in range(100):
            cachedb.add(inum)
        # 重新判断发现1已经不存在
        assert cachedb.exists("1") is False

    def test7(self):
        """simple_cache注解函数的测试。"""

        @cacheutils.simple_cache
        def say_hi7(name):
            """say hi to someone."""
            return "hi, {0}.".format(name)  # pylint: disable=consider-using-f-string

        res1 = say_hi7("n1")
        res2 = say_hi7("n2")
        res3 = say_hi7("n3")
        assert res1 == "hi, n1."
        assert res1 == res2
        assert res1 == res3
        assert say_hi7.__doc__ == "say hi to someone."

    def test8(self):
        """simple_cache注解类方法的测试。"""

        class TempClass:
            """临时测试类。"""

            @cacheutils.simple_cache
            def say_hi8(self, name):
                """just say_hi."""
                # pylint: disable=consider-using-f-string
                return "hello, {0}.".format(name)

        tmp1 = TempClass()
        res1 = tmp1.say_hi8("n1")
        res2 = tmp1.say_hi8("n2")
        res3 = tmp1.say_hi8("n3")
        assert res1 == "hello, n1."
        assert res1 == res2
        assert res1 == res3
        assert tmp1.say_hi8.__doc__ == "just say_hi."

    def test9(self):
        """simple_cache无参数的测试"""

        @cacheutils.simple_cache
        def say_hi9():
            return "hi"

        res1 = say_hi9()
        res2 = say_hi9()
        res3 = say_hi9()
        assert res1 == "hi"
        assert res1 == res2
        assert res1 == res3

    def test10(self):
        """同一个函数，使用别名或引用后，仍然视为同一个函数。使用相同的缓存键。"""

        def say_hi():
            return "just say hi to you..."

        hia = say_hi
        hib = say_hi

        hiaa = cacheutils.simple_cache(hia)
        hibb = cacheutils.simple_cache(hib)

        res1 = hiaa()
        res2 = hibb()
        assert res1 == res2

    def test11(self):
        """测试simple_cache作用于类成员方法时，多个实例间是否使用相同缓存。"""

        class RandomValueGenerator11:
            """测试类。"""

            @cacheutils.simple_cache
            def value(self):
                """返回随机数。"""
                return random.randint(1, 1000000)

        gen0 = RandomValueGenerator11()
        value0 = gen0.value()
        gens = []
        for _ in range(5):
            genx = RandomValueGenerator11()
            gens.append(genx)
            assert id(genx) != id(gen0)
            assert id(genx.value) != id(gen0.value)
            assert genx.value() == value0
