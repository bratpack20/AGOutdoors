#!/usr/bin/env python
# -*- coding: utf8 -*-
"""字典类型工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
from functools import partial
from .baseutils import Null

__all__ = [
    "fix_object",
    "to_object",
    "Object",
    "deep_merge",
    "select",
    "touch",
    "attrgetorset",
    "attrset",
    "update",
    "ignore_none_item",
    "change",
    "changes",
    "prefix_key",
    "diff",
    "HttpHeadersDict",
]


def fix_object(data):
    """Object内部数据变更时修正Object对象。"""
    if isinstance(data, dict):
        keys = list(data.keys())
        for key in keys:
            data[key] = to_object(data[key])
    elif isinstance(data, list):
        datasize = len(data)
        for index in range(datasize):
            data[index] = to_object(data[index])
    elif isinstance(data, set):
        data2 = list(data)
        data.clear()
        for item in data2:
            data.add(to_object(item))


def to_object(data):
    """转化为Object对象。"""
    if isinstance(data, Object):
        return data
    elif isinstance(data, dict):
        result = Object()
        for key, value in data.items():
            if isinstance(value, dict):
                value = to_object(value)
            result[key] = value
            setattr(result, key, value)
        return result
    elif isinstance(data, list):
        datasize = len(data)
        for index in range(datasize):
            data[index] = to_object(data[index])
        return data
    elif isinstance(data, set):
        data = list(data)
        datasize = len(data)
        for index in range(datasize):
            data[index] = to_object(data[index])
        return set(data)
    elif isinstance(data, tuple):
        data = list(data)
        datasize = len(data)
        for index in range(datasize):
            data[index] = to_object(data[index])
        return tuple(data)
    return data


class Object(dict):
    """Dict object allow use dot path selector.

    使用案例一:

    ```
        In [32]: from zenutils import dictutils

        In [33]: config = dictutils.Object()

        In [34]: config.listen = ('0.0.0.0', 6379)

        In [35]: config.listen
        Out[35]: ('0.0.0.0', 6379)

        In [36]: config['listen']
        Out[36]: ('0.0.0.0', 6379)

        In [39]: config['debug'] = True

        In [40]: config.debug
        Out[40]: True
    ```

    使用案例二：

    可以基于dictutils.Object构建Config类，方便业务开发中直接以属性方式使用配置项。

    ```
    class Config(dictutils.Object):
        def __init__(self, *args, **kwargs):
            self.item1 = "default value 1"
            self.item2 = {
                "subitem1": "default value 21",
                "subitem2": "default value 22",
            }
            super(Config, self).__init__(*args, **kwargs)

    config = Config()
    assert config.item1 == "default value 1"
    assert config.item2.subitem1 == "default value 21"
    assert config.item2.subitem2 == "default value 22"
    ```

    注意：

    1. dictutils.Object([1, 2, 3])将报错。初始化数据的顶层必须为dict类型。
    2. dictutils.Object({"a": [1, 2, 3]})是允许的。
    3. Config初始化时，属性默认值赋值必须在super().__init__()之前。否则，会把外部传入的属性值给屏蔽掉。

    """

    def __init__(self, *args, **kwargs):
        super(Object, self).__init__(*args, **kwargs)
        fix_object(self)
        for key, value in self.items():
            setattr(self, key, value)

    def __setitem__(self, key, value):
        if not isinstance(value, self.__class__):
            value = to_object(value)
        result = super(Object, self).__setitem__(key, value)
        self.__dict__[key] = value
        return result

    def __setattr__(self, name, value):
        if not isinstance(value, self.__class__):
            value = to_object(value)
        self[name] = value
        result = super(Object, self).__setattr__(name, value)
        return result

    def fix(self):
        """修正自己，将自己名下的所有子元素，都尽可能得转化为Object实例。"""
        fix_object(self)
        return self

    def update(self, *args, **kwargs):
        result = super(Object, self).update(*args, **kwargs)
        fix_object(self)
        return result

    def pop(self, key, default=Null):
        if default == Null:
            result = super(Object, self).pop(key)
        else:
            result = super(Object, self).pop(key, default)
        if hasattr(self, key):
            delattr(self, key)
        return result

    def popitem(self):
        key, value = super(Object, self).popitem()
        if hasattr(self, key):
            delattr(self, key)
        return key, value

    def setdefault(self, key, default=None):
        super(Object, self).setdefault(key, default)
        fix_object(self)

    def clear(self):
        keys = list(super(Object, self).keys())
        result = super(Object, self).clear()
        for key in keys:
            if hasattr(self, key):
                delattr(self, key)
        return result

    def copy(self):
        return Object(super(Object, self).copy())

    def select(self, path, default_value=None):
        """根据路径获取Object下的元素值。"""
        data = self
        paths = path.split(".")
        for path in paths:
            if isinstance(data, dict) and path in data:
                data = data[path]
            elif (
                isinstance(data, (list, tuple))
                and path.isdigit()
                and int(path) < len(data)
            ):
                data = data[int(path)]
            elif hasattr(data, path):
                data = getattr(data, path)
            else:
                return default_value
        return data


def deep_merge(target, data):
    """Merge the second dict into the first one deeply. Always returns the first dict reference.

    Example:

    In [14]: from zenutils import dictutils

    In [15]: data1 = {"a": {"b": {"c": "c"}}}

    In [16]: data2 = {"a": {"b": {"d": "d"}}}

    In [17]: dictutils.deep_merge(data1, data2)

    In [18]: data1
    Out[18]: {'a': {'b': {'c': 'c', 'd': 'd'}}}
    """
    for key2, value2 in data.items():
        value1 = target.get(key2, None)
        if isinstance(value1, dict) and isinstance(value2, dict):
            deep_merge(value1, value2)
        else:
            target[key2] = value2
    return target


def select(data, path, default_value=None, slient=True):
    """Get field value in dot sperated path.

    Example:

    In [6]: from zenutils import dictutils

    In [7]: data = {
    ...: "a": {
    ...:     "b": {
    ...:         "c": "abc",
    ...:     }
    ...: }
    ...: }

    In [8]: dictutils.select(data, "a.b.c")
    Out[8]: 'abc'

    """

    def _(value, slient, path):
        if slient:
            return value
        else:
            raise KeyError(path)

    default = partial(_, default_value, slient, path)
    names = path.split(".")
    node = data
    for name in names:
        if isinstance(node, dict):
            try:
                node = node[name]
            except:  # pylint: disable=bare-except
                return default()
        elif isinstance(node, list) and name.isdigit():
            try:
                node = node[int(name)]
            except:  # pylint: disable=bare-except
                return default()
        elif hasattr(node, name):
            node = getattr(node, name)
        else:
            return default()
    return node


def touch(data, path, default_value):
    """Make sure data has the path.
    If data has the path, return the orignal value.
    If data NOT has the path, create a new path, and set to default_value, returns the default value.
    """
    result = select(data, path, Null)
    if result == Null:
        update(data, path, default_value)
        return default_value
    else:
        return result


def attrgetorset(data, key, default_value):
    """Get or set attr to data directly, and the key is a one level key.
    If data contains the key, get the original value.
    If data NOT contains the key, set the key to the default value.
    """
    if isinstance(data, dict):
        if not key in data:
            data[key] = default_value
        return data[key]
    elif isinstance(data, list):
        key = int(key)
        if key >= len(data):
            for _ in range(key + 1 - len(data)):
                data.append(None)
            data[key] = default_value
        return data[key]
    else:
        if not hasattr(data, key):
            setattr(data, key, default_value)
        return getattr(data, key)


def attrset(data, key, value):
    """Set attr to data directory, and the key is a one level key.
    If data contains the key, overrdie the original value with the new value.
    If data NOT contains the key, add a new key to the new value.
    """
    if isinstance(data, dict):
        data[key] = value
    elif isinstance(data, list):
        key = int(key)
        if key >= len(data):
            for _ in range(key + 1 - len(data)):
                data.append(None)
        data[key] = value
    else:
        setattr(data, key, value)


def update(data, path, value):
    """Set attr to data, and the key is a dot-seperated-path.

    If data contains the key, override the original value with the new value.
    If data NOT contains the key, add a new key to the new value.


    """
    old_data = data
    is_object = isinstance(data, Object)
    paths = path.split(".")
    for index in range(0, len(paths) - 1):
        path = paths[index]
        path_next = paths[index + 1]
        if path_next.isdigit():
            next_empty_value = []
        else:
            if is_object:
                next_empty_value = Object()
            else:
                next_empty_value = {}
        data = attrgetorset(data, path, next_empty_value)
    path = paths[-1]
    attrset(data, path, value)
    return old_data


def ignore_none_item(data):
    """Returns a new dict that only contains empty-value field.

    None, empty list, empty dict: are treat as empty values.
    0, empty string, False: are NOT empty values.

    Example:

    In [3]: from zenutils import dictutils

    In [4]: data = {
    ...: "a": "",
    ...: "b": None,
    ...: "c": 0,
    ...: "d": False,
    ...: "e": [],
    ...: "f": {},
    ...: }

    In [5]: dictutils.ignore_none_item(data)
    Out[5]: {'a': '', 'c': 0, 'd': False}
    """
    result = {}
    for key, value in data.items():
        if value is None:
            continue
        if not value:
            if isinstance(value, (list, dict)):
                continue
        result[key] = value
    return result


def change(
    object_instance,
    data_dict,
    object_key,
    dict_key=None,
    do_update=True,
    ignore_empty_value=False,
):
    """Update property value of object_instance, using the value from data_dict.

    If value changed, return True.
    If value is equals, return False.
    """
    dict_key = dict_key or object_key
    if isinstance(object_instance, dict):
        object_value = object_instance.get(object_key, None)
    else:
        object_value = getattr(object_instance, object_key, None)
    if isinstance(data_dict, dict):
        dict_value = data_dict.get(dict_key, None)
    else:
        dict_value = getattr(data_dict, dict_key, None)
    if (object_value == dict_value) or (
        ignore_empty_value
        and (object_value == "" or (object_value is None))
        and (dict_value == "" or (dict_value is None))
    ):
        return False
    else:
        if do_update:
            if isinstance(object_instance, dict):
                object_instance[object_key] = dict_value
            else:
                setattr(object_instance, object_key, dict_value)
        return True


def changes(
    object_instance,
    data_dict,
    keys,
    return_changed_keys=False,
    do_update=True,
    ignore_empty_value=False,
):
    """Update property values of object_instance, using the value form data_dict.

    If any property changed, return True.
    If values are equal, return False.
    keys is a list of string or string pair.
    """
    result = False
    changed_keys = []
    for key in keys:
        if isinstance(key, (tuple, set, list)) and len(key) > 1:
            object_key = key[0]
            dict_key = key[1]
        else:
            object_key = key
            dict_key = None
        changed = change(
            object_instance,
            data_dict,
            object_key,
            dict_key,
            do_update=do_update,
            ignore_empty_value=ignore_empty_value,
        )
        if changed:
            changed_keys.append(object_key)
            result = True
    if return_changed_keys:
        return result, changed_keys
    else:
        return result


def prefix_key(data, prefix):
    """Add a prefix for all keys.

    Example:

    In [41]: from zenutils import dictutils

    In [42]: dictutils.prefix_key({"id": 1, "name": "mktg"}, 'department')
    Out[42]: {'departmentId': 1, 'departmentName': 'mktg'}

    """
    data2 = {}
    for key, value in data.items():
        key = prefix + key.capitalize()
        data2[key] = value
    return data2


def diff(object_instance1, object_instance2):
    """Find keys that changed. Returns: created_keys, updated_keys, deleted_keys"""
    deleted_keys = []
    updated_keys = []
    created_keys = []

    keys1 = set(object_instance1.keys())
    keys2 = set(object_instance2.keys())

    deleted_keys = list(keys1 - keys2)
    created_keys = list(keys2 - keys1)
    both_keys = keys1.intersection(keys2)
    for key in both_keys:
        if object_instance1[key] != object_instance2[key]:
            updated_keys.append(key)

    return created_keys, updated_keys, deleted_keys


class HttpHeadersDict(object):
    """HTTP请求头字典。

    由于HTTP请求头允许同名，且有序，所以不能直接使用python中的dict字典进行数据存储。
    这里使用typing.List[typing.Tuple[str, str]]结构保存请求头数据。
    并对外提供get, getlist, create_header, add_header, delete_header, replace_header等操作方式。
    """

    def __init__(self, data=None):
        self.data = []
        if isinstance(data, dict):
            for key, value in data.items():
                self.data.append((key, value))
        elif isinstance(data, list):
            for key, value in data:
                self.data.append((key, value))

    def create_header(self, name, value):
        """创建一个新的请求头。

        如果请求头重名，则不创建，并返回False。
        如果请求头不重名，则创建。
        """
        name = name.title()
        datasize = len(self.data)
        for index in range(datasize):
            if self.data[index][0] == name:
                return False
        self.data.append((name, value))
        return True

    def add_header(self, name, value):
        """追加一个请求头。

        不检验请求头是重命名，直接追加。

        注意：
        1. HTTP请求头没有特殊要求，是可以重复添加的。
        2. 但对一些特殊的请求头，如Host，则不允许重复添加。否则，nginx服务器会拒绝该请求，并报400错误.
        """
        name = name.title()
        self.data.append((name, value))
        return True

    def delete_header(self, name):
        """删除请求头。如果有多个同名请求头，则全部删除。

        当被删除的请求头被成功删除时，返回True。
        如果要求puch删除的请求头不存在时，则返回False。
        """
        name = name.title()
        for index in range(len(self.data) - 1, -1, -1):
            if self.data[index][0] == name:
                del self.data[index]
                return True
        return False

    def replace_header(self, name, value):
        """替换请求头。

        如果原来只有一个同名请求头，则替换。
        如果原来没有同名请求头，则创建。
        如果原来有多个请求头，则替换第一个，删除其他所有同名请求头。
        """
        name = name.title()
        delete_flag = False
        new_flag = True
        for index in range(len(self.data) - 1, -1, -1):
            if self.data[index][0] == name:
                if delete_flag:
                    del self.data[index]
                else:
                    self.data[index] = (name, value)
                    delete_flag = True
                    new_flag = False
        if new_flag:
            self.data.append((name, value))
        return True

    def get(self, name):
        """获取请求头值。

        如果有多个同名请求头，则返回最后一个值。
        """
        name = name.title()
        for index in range(len(self.data) - 1, -1, -1):
            if self.data[index][0] == name:
                return self.data[index][1]
        return None

    def getlist(self, name):
        """以列表形式返回所有同名请求头的值。"""
        name = name.title()
        values = []
        datasize = len(self.data)
        for index in range(datasize):
            if self.data[index][0] == name:
                values.append(self.data[index][1])
        return values
