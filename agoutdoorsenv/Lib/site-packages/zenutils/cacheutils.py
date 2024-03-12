#!/usr/bin/env python
# -*- coding: utf8 -*-
"""缓存相关工具。
"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
import functools
from .sixutils import force_text

__all__ = [
    "simple_cache",
    "ReqIdCache",
    "get_cached_value",
    "cache",
]


def get_cached_value(holder_object, cache_key, getter, *args, **kwargs):
    """Get cached value from a holder_object and set the cache value at the first request.

    @Returns:
        (Any): The cached value or the getter returned value.

    @Parameters:
        holder_object(Any): The holder object which holds the cache property.
        cache_key(str): The cache property which will attach to the holder object.
        getter(Callable): The callable object which will be called if there is no cache value.
        *args(Any): Place holder parameters which will be used by getter.
        **kwargs(Any): Keyword parameters which will be used by getter.

    @Example:
        token = request.GET.get("token")
        value = get_cached_value(request, "cache_key_for_get_user_info", services.get_user_info, token=token)
    """
    cache_key = force_text(cache_key)
    if not hasattr(holder_object, cache_key):
        setattr(holder_object, cache_key, getter(*args, **kwargs))
    return getattr(holder_object, cache_key)


class _GlobalSimpleCacheHolder:
    """未指定缓存位置时，默认的存放位置。"""


# 未指定缓存位置时，默认的存放位置。
_global_simple_cache_holder = _GlobalSimpleCacheHolder()


def simple_cache(func):
    """简单的函数结果缓存。

    @Example:

    ```
        @cacheutils.simple_cache
        def hi(name):
            return "hi, " + name
    ```

    注意：
    1. 永久缓存。
    2. 不根据参数分别缓存，所以只有第一次调用的参数有效。
    3. 未加锁。如果在多线程环境下，函数可能会被多次执行，最终结果也可能会相互覆盖。
    4. 一个函数，使用别名或引用后，再进行调用，仍然视为同一个函数，使用相同的缓存健。
    5. 如果函数抛出异常，则不会被缓存。
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        key = repr(func)
        if hasattr(_global_simple_cache_holder, key):
            return getattr(_global_simple_cache_holder, key)
        result = func(*args, **kwargs)
        setattr(_global_simple_cache_holder, key, result)
        return result

    return inner


def cache(holder_object=None, cache_key=None):
    """函数结果缓存。

    需要指定存放位置和缓存键。
    如果不指定的话，则认为缓存存放位置及缓存键在函数的前导参数中。
    如果不需要进行缓存存放位置及缓存键的控制，可以使用simple_cache替代。

    @Returns:
        (Any): The cached value or the returned value.

    @Parameters:
        holder_object(Any): The holder object which holds the cache property.
        cache_key(str): The cache property which will attach to the holder object.

    @Notice:
        If your only give one parameter, then the parameter will be treated as cache_key.

    @Example:
        a = Object()
        @cacheutils.cache(a, "_num")
        def getNum():
            return random.randint(0, 10)
        v1 = getNum()
        v2 = getNum()
        v3 = getNum()
        assert v1 == v2 == v3

    @Example:
        @cacheutils.cache("_num")
        def getNum():
            return random.randint(0, 10)
        a = Object()
        v1 = getNum(a)
        v2 = getNum(a)
        v3 = getNum(a)
        assert v1 == v2 == v3

    @Example:
        @cacheutils.cache()
        def getNum():
            return random.randint(0, 10)
        a = Object()
        v1 = getNum(a, "_num")
        v2 = getNum(a, "_num")
        v3 = getNum(a, "_num")
        assert v1 == v2 == v3
    """

    if holder_object and cache_key is None:
        cache_key = holder_object
        holder_object = None

    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            # 当你在局部函数中修改某个变量的值时
            # 那这个变量就成了这个局部函数局部变量
            # 所以在这个变量被赋值前
            # 也无法继承宿主函数的变量值
            # 所以我们这里需要引入holder_object_inner
            # 这样以来在inner函数中就没有对holder_object变量的任何修改
            # 这时在inner函数中就可以取出宿主函数变量holder_object
            if (holder_object is None) and (cache_key is None):
                holder_object_inner = args[0]
                cache_key_inner = args[1]
                args = args[2:]
            elif holder_object is None:
                holder_object_inner = args[0]
                cache_key_inner = cache_key
                args = args[1:]
            else:
                holder_object_inner = holder_object
                cache_key_inner = cache_key
            if hasattr(holder_object_inner, cache_key_inner):
                return getattr(holder_object_inner, cache_key_inner)
            else:
                result = func(*args, **kwargs)
                setattr(holder_object_inner, cache_key_inner, result)
                return result

        return inner

    return outer


class ReqIdCache(object):
    """用于reqid的缓存。

    基本思路是分批保存，分批清理。
    """

    def __init__(self, bucket_size=100 * 10000, bucket_cout=10):
        self.bucket_size = bucket_size
        self.bucket_count = bucket_cout
        self.buckets = []
        for _ in range(self.bucket_count):
            self.buckets.append(set())
        self.current_bucket = 0

    def add(self, reqid):
        """将新的reqid添加到缓存池中。"""
        if len(self.buckets[self.current_bucket]) >= self.bucket_size:
            # 循环使用n个缓存池。
            self.current_bucket += 1
            self.current_bucket = self.current_bucket % self.bucket_count
            self.buckets[self.current_bucket] = set()
        self.buckets[self.current_bucket].add(reqid)

    def exists(self, reqid):
        """判断当前reqid是否在缓存池中。"""
        for i in range(self.bucket_count):
            if reqid in self.buckets[i]:
                return True
        return False
