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

import unittest
from zenutils import listutils
from zenutils.sixutils import BYTES_TYPE, STR_TYPE


class TestListUtils(unittest.TestCase):
    def test01(self):
        data = [1, 2, 3, 4]
        data2 = listutils.chunk(data, 3)
        assert data2[0] == [1, 2, 3]

    def test02(self):
        data = [1, 2, 3, 4]
        data2 = listutils.chunk(data, 2)
        assert data2[0] == [1, 2]
        assert data2[1] == [3, 4]
        assert len(data2) == 2

    def test03(self):
        data = [1, 2, 3, 4]
        data2 = listutils.chunk(data, 2, with_padding=True)
        assert data2[0] == [1, 2]
        assert data2[1] == [3, 4]
        assert len(data2) == 2

    def test04(self):
        data = [1, 2, 3, 4]
        data2 = listutils.chunk(data, 3, with_padding=True)
        assert data2[0] == [1, 2, 3]
        assert data2[1] == [4, None, None]
        assert len(data2) == 2

    def test05(self):
        data = []
        listutils.pad(data, 3, 1)
        assert data == [1, 1, 1]

    def test06(self):
        data = [1]
        listutils.pad(data, 3, 1)
        assert data == [1, 1, 1]

    def test07(self):
        data = [1, 1]
        listutils.pad(data, 3, 1)
        assert data == [1, 1, 1]

    def test08(self):
        data = [1, 1, 1]
        listutils.pad(data, 3, 1)
        assert data == [1, 1, 1]

    def test09(self):
        data = [1, 1, 1, 1]
        listutils.pad(data, 3, 1)
        assert data == [1, 1, 1, 1]

    def test10(self):
        assert listutils.clean_none([]) == []
        assert listutils.clean_none([1]) == [1]
        assert listutils.clean_none([1, 2]) == [1, 2]
        assert listutils.clean_none([1, None, 2]) == [1, 2]
        assert listutils.clean_none([1, None, 2, None]) == [1, 2]

    def test11(self):
        assert listutils.unique([]) == []
        assert listutils.unique([1]) == [1]
        assert listutils.unique([1, 1]) == [1]
        assert listutils.unique([1, 2]) == [1, 2]
        assert listutils.unique([1, 2, 3]) == [1, 2, 3]
        assert listutils.unique([1, 2, 2]) == [1, 2]

    def test12(self):
        thelist = [1, 2, 3]
        map = {
            1: "a",
            2: "b",
            3: "c",
            4: "d",
        }
        assert listutils.replace(thelist, map) == ["a", "b", "c"]

    def test13(self):
        thelist = [1, 2, 3]
        map = {
            1: "a",
            2: "b",
            3: "c",
            4: "d",
        }
        newlist = listutils.replace(thelist, map, inplace=False)
        assert newlist == ["a", "b", "c"]
        assert thelist == [1, 2, 3]

    def test14(self):
        thelist = [1, 2, 3]
        map = {}
        assert listutils.replace(thelist, map) == [1, 2, 3]

    def test15(self):
        thelist = 1, 2, 3
        map = {
            1: "a",
        }
        assert listutils.replace(thelist, map) == ["a", 2, 3]

    def test15_01(self):
        thelist = [1, 2, 3]
        map = {1: 4}
        listutils.replace(thelist, map, True)
        assert thelist == [4, 2, 3]

    def test16(self):
        thelist = [1, 2, 3]
        listutils.append_new(thelist, 1)
        listutils.append_new(thelist, 2)
        listutils.append_new(thelist, 3)
        listutils.append_new(thelist, 4)
        assert thelist == [1, 2, 3, 4]

    def test17(self):
        thelist = ["a", "b", "c", "a", "b", "b"]
        info = listutils.group(thelist)
        assert info["a"] == 2
        assert info["b"] == 3
        assert info["c"] == 1

    def test18(self):
        old_list = [1, 2, 3]
        new_list = [2, 3, 4]

        set_new, set_delete, set_update = listutils.compare(old_list, new_list)
        assert set_new == set([4])
        assert set_delete == set([1])
        assert set_update == set([2, 3])

    def test19(self):
        old_list = []
        new_list = [2, 3, 4]

        set_new, set_delete, set_update = listutils.compare(old_list, new_list)
        assert set_new == set([2, 3, 4])
        assert set_delete == set([])
        assert set_update == set([])

    def test20(self):
        old_list = [1, 2, 3]
        new_list = [4, 5, 6]

        set_new, set_delete, set_update = listutils.compare(old_list, new_list)
        assert set_new == set([4, 5, 6])
        assert set_delete == set([1, 2, 3])
        assert set_update == set([])

    def test21(self):
        old_list = [1, 2, 3]
        new_list = []

        set_new, set_delete, set_update = listutils.compare(old_list, new_list)
        assert set_new == set([])
        assert set_delete == set([1, 2, 3])
        assert set_update == set([])

    def test22(self):
        data1 = [None, True, False]
        assert listutils.first(*data1) == True

        data2 = [None, False, True]
        assert listutils.first(*data2) == False

        data3 = [None, None, None]
        assert listutils.first(*data3) == None

        def is_empty_str(value):
            if value is None:
                return None
            if isinstance(value, (STR_TYPE, BYTES_TYPE)):
                value = value.strip()
                if value:
                    return value
            return None

        data4 = ["", "   ", None, False, True, 1234, "hello"]
        assert listutils.first(*data4, check=is_empty_str, default="world") == "hello"

        data5 = ["", "   ", None, False, True, 1234]
        assert listutils.first(*data5, check=is_empty_str, default="world") == "world"

    def test23(self):
        data1 = "abca"
        data2 = listutils.replace(data1, {"a": "x"})
        assert data2[0] == "x"
        assert data2[1] == "b"
        assert data2[2] == "c"
        assert data2[3] == "x"

    def test24(self):
        thelists = [
            ("a", "b", "c"),
            ("a", "e", "b"),
            ("a", "e", "c"),
            ("a", "e", "f"),
            ("a", "f", "d"),
            ("a", "b", "d"),
            ("b", "d", "c"),
        ]
        result = listutils.topological_sort(*thelists)
        for rule in thelists:
            assert listutils.topological_test(result, rule) == True

    def test25(self):
        assert listutils.topological_test([1, 2, 3], [1, 2]) == True
        assert listutils.topological_test([1, 2, 3], [1, 3]) == True
        assert listutils.topological_test([1, 2, 3], [2, 3]) == True
        assert listutils.topological_test([1, 2, 3], [2, 1]) == False
        assert listutils.topological_test([1, 2, 3], [3, 1]) == False
        assert listutils.topological_test([1, 2, 3], [3, 2]) == False

    def test26(self):
        thelists = [
            ("a", "b", "c"),
            ("b", "e", "g"),
            ("c", "f", "g"),
            ("f", "d", "g"),
        ]
        result = listutils.topological_sort(*thelists)
        for rule in thelists:
            assert listutils.topological_test(result, rule) == True

    def test27(self):
        thelists = [
            ("a"),
            ("b"),
            ("c"),
            ("a", "x"),
            ("f", "o", "x"),
            ("c", "a", "t"),
        ]
        result = listutils.topological_sort(*thelists)
        for rule in thelists:
            assert listutils.topological_test(result, rule) == True

    def test28(self):
        thelist = [1, 2, 3]
        info = listutils.list2dict(thelist, ["a", "b", "c"])
        assert info["a"] == 1
        assert info["b"] == 2
        assert info["c"] == 3

    def test29(self):
        thelist = [1, 2, 3]
        info = listutils.list2dict(thelist, ["a", "b"])
        assert info["a"] == 1
        assert info["b"] == 2
        assert len(info) == 2

    def test30(self):
        thelist = [1, 2, 3]
        info = listutils.list2dict(thelist, ["a", "b", "c", "d"])
        assert info["a"] == 1
        assert info["b"] == 2
        assert info["c"] == 3
        assert info["d"] is None

    def test31(self):
        thelist = [1, 2, 3]
        info = listutils.list2dict(thelist, ["a", ("b", "b"), ["c"], ("d", "d")])
        assert info["a"] == 1
        assert info["b"] == 2
        assert info["c"] == 3
        assert info["d"] == "d"

    def test32(self):
        thelist = [1, 3, 2]
        assert listutils.is_ordered(thelist) is False

    def test33(self):
        thelist = [3, 2, 1]
        assert listutils.is_ordered(thelist, reverse=True) is True

    def test34(self):
        thelist = [3, 4, 1]
        assert listutils.is_ordered(thelist, reverse=True) is False

    def test35(self):
        thelist = []
        assert listutils.is_ordered(thelist) is True
        assert listutils.is_ordered(thelist, reverse=True) is True

    def test36(self):
        old_list = [1, 2, 3]
        new_list = [2, 3, 4]

        created, deleted, changed = listutils.compare_execute(
            old_data=old_list,
            new_data=new_list,
            create_callback=lambda key, data: data,
            delete_callback=lambda key, instance: instance,
            change_callback=lambda key, instance, data: instance,
            old_key=lambda x: x,
        )
        assert created == [4]
        assert deleted == [1]
        assert changed == [2, 3]

    def test37(self):
        old_list = [1, 2, 3]
        new_list = [3, 4, 5]

        def do_create(key, data):
            if data > 4:
                return data
            else:
                return None

        def do_delete(key, instance):
            if instance > 1:
                return instance
            else:
                return None

        def do_change(key, instance, data):
            return None

        created, deleted, changed = listutils.compare_execute(
            old_data=old_list,
            new_data=new_list,
            create_callback=do_create,
            delete_callback=do_delete,
            change_callback=do_change,
            old_key=lambda x: x,
        )
        assert created == [5]
        assert deleted == [2]
        assert changed == []
