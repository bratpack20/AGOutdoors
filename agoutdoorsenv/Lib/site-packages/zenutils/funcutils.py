#!/usr/bin/env python
# -*- coding: utf8 -*-
"""魔法工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
import re
import time
import json
import functools
import logging

try:
    from inspect import signature
    from inspect import isclass
    import inspect
except ImportError:
    from inspect2 import signature  # required by python 2.7 and python 3.2
    from inspect2 import isclass
    import inspect2 as inspect

from .sixutils import PY2
from .sixutils import Interrupted

__all__ = [
    "inspect",
    "signature",
    "isclass",
    "get_default_values",
    "get_inject_params",
    "call_with_inject",
    "mcall_with_inject",
    "classproperty",
    "chain",
    "BunchCallable",
    "try_again_on_error",
    "get_builtins_dict",
    "get_all_builtin_exceptions",
    "get_class_name",
    "ChainableProxy",
    "is_a_class",
    "get_method_help",
    "get_method_signature",
]

logger = logging.getLogger(__name__)


def get_default_values(func):
    """Get function parameters default value.

    In [1]: from zenutils import funcutils

    In [2]: def hi(name, msg="hi, {name}"):
    ...:     print(msg.format(name=name))
    ...:

    In [3]: funcutils.get_default_values(hi)
    Out[3]: {'msg': 'hi, {name}'}
    """
    data = {}
    parameters = signature(func).parameters
    for name, parameter in parameters.items():
        if parameter.default != parameter.empty:
            data[name] = parameter.default
    return data


def get_inject_params(func, data, raise_on_missing_field=True):
    """Get all params that required by calling the func from data.

    In [1]: from zenutils import funcutils

    In [2]: def hi(name, msg="hi, {name}"):
    ...:     print(msg.format(name=name))
    ...:

    In [3]: params = funcutils.get_inject_params(hi, data)

    In [4]: params
    Out[4]: {'name': 'Cissie', 'msg': 'hi, {name}'}

    In [5]: hi(**params)
    hi, Cissie

    """
    from zenutils import typingutils

    params = {}
    parameters = signature(func).parameters
    for name, parameter in parameters.items():
        if parameter.kind == 2:  # 无法处理*args这样的占位参数，忽略他们
            continue
        if parameter.default is parameter.empty:
            # no default value, this parameter is required
            if not name in data:
                if raise_on_missing_field:
                    raise KeyError("Missing parameter: {name}".format(name=name))
                else:
                    continue
            value = data[name]
        else:
            value = data.get(name, parameter.default)
        if not parameter.annotation is parameter.empty:
            value = typingutils.smart_cast(parameter.annotation, value, field_name=name)
        params[name] = value
    return params


def call_with_inject(func, data):
    """函数智能调用。

    根据函数定义，自动从data中提取参数，进行函数调用。
    """
    raise_on_missing_field = True
    args = data.get("_inject_args", []) or []  # 获取位置参数
    if len(args):
        raise_on_missing_field = False  # 如果已经有位置参数，无法正确判断是否有字段缺失的情况，则在获取关键字参数时就不再抛出异常
    kwargs = get_inject_params(
        func, data, raise_on_missing_field=raise_on_missing_field
    )
    try:
        return func(*args, **kwargs)
    except Exception as error:
        logger.debug(
            "call_with_inject failed: args=%s, kwargs=%s, error_message=%s",
            args,
            kwargs,
            error,
        )

        raise error


def mcall_with_inject(funcs, data):
    """多函数智能调用。

    使用data中的参数，自动对多个函数进行智能调用。结果以数组形式返回。
    """
    if not isinstance(funcs, (list, set, tuple)):
        funcs = [funcs]
    results = []
    for func in funcs:
        params = get_inject_params(func, data)
        result = func(**params)
        results.append(result)
    return results


class ClassPropertyDescriptor(object):
    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func):
    """classproperty decorator.

    class Bar(object):

        _bar = 1

        @classproperty
        def bar(cls):
            return cls._bar

        @bar.setter
        def bar(cls, value):
            cls._bar = value


    # test instance instantiation
    foo = Bar()
    assert foo.bar == 1

    baz = Bar()
    assert baz.bar == 1

    # test static variable
    baz.bar = 5
    assert foo.bar == 5

    # test setting variable on the class
    Bar.bar = 50
    assert baz.bar == 50
    assert foo.bar == 50
    """
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


class chain(object):
    """ """

    def __init__(self, *args):
        self.funcs = args

    def __call__(self, init_result, extra_args=None, extra_kwargs=None):
        extra_args = extra_args or []
        extra_kwargs = extra_kwargs or {}
        result = init_result
        for func in self.funcs:
            if func and callable(func):
                result = func(result, *extra_args, **extra_kwargs)
        return result


class BunchCallable(object):
    def __init__(self, *args, **kwargs):
        """BunchCallable init.

        @Returns:
            (None)

        @Parameters:
            args(Any, multiple):
            return_callback_results(bool, optional, default to False):
        """
        return_callback_results = kwargs.get("return_callback_results", False)
        self.return_callback_results = return_callback_results
        self.funcs = []
        for func in args:
            if isinstance(func, self.__class__):
                self.funcs += func.funcs
            else:
                self.funcs.append(func)

    def __call__(self, *args, **kwargs):
        results = []
        for func in self.funcs:
            if func and callable(func):
                result = func(*args, **kwargs)
            else:
                result = None
            results.append(result)
        if self.return_callback_results:
            return results
        else:
            return None


def try_again_on_error(
    sleep=5, limit=0, callback=None, callback_args=None, callback_kwargs=None
):
    """当遇到错误时，重新尝试。"""

    def outter_wrapper(func):
        def wrapper(*args, **kwargs):
            counter = 0
            while True:
                counter += 1
                try:
                    return func(*args, **kwargs)
                except Interrupted:
                    logger.info("exit on got InterruptedError...")
                    break
                except Exception as error:  # pylint: disable=broad-exception-caught
                    logger.exception("got unknown exception: %s", str(error))
                    if callback:
                        logger.info(
                            "call callback function %s with params %s %s",
                            str(callback),
                            str(callback_args),
                            str(callback_kwargs),
                        )
                        local_callback_args = callback_args or []
                        local_callback_kwargs = callback_kwargs or {}
                        callback(*local_callback_args, **local_callback_kwargs)
                    time.sleep(sleep)
                if limit and counter >= limit:
                    break

        return functools.wraps(func)(wrapper)

    return outter_wrapper


def get_builtins_dict():
    """Get builtins data as dict typed.

    @Returns:
        (dict): All data in builtins.

    """
    data = {}
    if PY2:  # no updates anymore...
        # keys are __builtins__ of python 2.7.18
        keys = [
            "ArithmeticError",
            "AssertionError",
            "AttributeError",
            "BaseException",
            "BufferError",
            "BytesWarning",
            "DeprecationWarning",
            "EOFError",
            "Ellipsis",
            "EnvironmentError",
            "Exception",
            "False",
            "FloatingPointError",
            "FutureWarning",
            "GeneratorExit",
            "IOError",
            "ImportError",
            "ImportWarning",
            "IndentationError",
            "IndexError",
            "KeyError",
            "KeyboardInterrupt",
            "LookupError",
            "MemoryError",
            "NameError",
            "None",
            "NotImplemented",
            "NotImplementedError",
            "OSError",
            "OverflowError",
            "PendingDeprecationWarning",
            "ReferenceError",
            "RuntimeError",
            "RuntimeWarning",
            "StandardError",
            "StopIteration",
            "SyntaxError",
            "SyntaxWarning",
            "SystemError",
            "SystemExit",
            "TabError",
            "True",
            "TypeError",
            "UnboundLocalError",
            "UnicodeDecodeError",
            "UnicodeEncodeError",
            "UnicodeError",
            "UnicodeTranslateError",
            "UnicodeWarning",
            "UserWarning",
            "ValueError",
            "Warning",
            "ZeroDivisionError",
            "__debug__",
            "__doc__",
            "__import__",
            "__name__",
            "__package__",
            "abs",
            "all",
            "any",
            "apply",
            "basestring",
            "bin",
            "bool",
            "buffer",
            "bytearray",
            "bytes",
            "callable",
            "chr",
            "classmethod",
            "cmp",
            "coerce",
            "compile",
            "complex",
            "copyright",
            "credits",
            "delattr",
            "dict",
            "dir",
            "divmod",
            "enumerate",
            "eval",
            "execfile",
            "exit",
            "file",
            "filter",
            "float",
            "format",
            "frozenset",
            "getattr",
            "globals",
            "hasattr",
            "hash",
            "help",
            "hex",
            "id",
            "input",
            "int",
            "intern",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "license",
            "list",
            "locals",
            "long",
            "map",
            "max",
            "memoryview",
            "min",
            "next",
            "object",
            "oct",
            "open",
            "ord",
            "pow",
            "print",
            "property",
            "quit",
            "range",
            "raw_input",
            "reduce",
            "reload",
            "repr",
            "reversed",
            "round",
            "set",
            "setattr",
            "slice",
            "sorted",
            "staticmethod",
            "str",
            "sum",
            "super",
            "tuple",
            "type",
            "unichr",
            "unicode",
            "vars",
            "xrange",
            "zip",
        ]
        for key in keys:
            try:
                data[key] = eval(key)
            except:
                pass
    else:
        import builtins

        for key in dir(builtins):
            data[key] = getattr(builtins, key)
    return data


def get_all_builtin_exceptions():
    """Get all builtin exceptions."""

    def get_exceptions(scope):
        klasses = set()
        for key, value in scope.items():
            if key.startswith("_"):
                continue
            try:
                if issubclass(value, BaseException):
                    klasses.add(value)
            except (
                TypeError
            ):  # some value can NOT be used in issubclass(xxx), just ignore it...
                pass
        return klasses

    es1 = get_exceptions(get_builtins_dict())
    es2 = get_exceptions(globals())
    es3 = get_exceptions(locals())
    return es1.union(es2).union(es3)


def get_class_name(klass, with_module=False):
    """Get a class's name.

    @Returns:
        (str): The name of the klass.

    @Parameters:
        klass(Any): A class or
    """
    if not is_a_class(klass):
        klass = klass.__class__
    if with_module:
        return klass.__module__ + "." + klass.__name__
    else:
        return klass.__name__


def retry(sleep=0, limit=3, exceptions=None, raise_exceptions=None, **kwargs):
    """Retry function on errors.

    @Parameters:
        sleep(int, default to 0):
            Sleep seconds after retry failed. 0 or less means no sleep.
        limit(int, default to 3):
            max try times.
        exceptions(list of exception types, default to [Exception] means all kind of exceptions):
            only retry on these errors, otherwise raise immediately.
        raise_exceptions(list of exception types, default to []):
            raise immediately for these exceptions.
        **kwargs:
            Update key parameters while doing retry.

    @Example:
        @retry(sleep=5, limit=3)
        def download(url, filename):
            response = requests.get(url)
            with open(filename, "wb") as fobj:
                fobj.write(response.content)
        download("http://zencore.cn/example.zip", "example.zip")
    """
    if isinstance(raise_exceptions, (list, set)):
        raise_exceptions = tuple(list(raise_exceptions))
    if isinstance(exceptions, (list, set)):
        exceptions = tuple(list(exceptions))

    def outter_wrapper(func):
        def wrapper(*func_args, **func_kwargs):
            last_error = None
            for i in range(limit):
                break_flag = None
                try:
                    if i > 0:
                        func_kwargs.update(**kwargs)
                        logger.warning(
                            "retry again on %s with last_error=%s...", func, last_error
                        )
                    return func(*func_args, **func_kwargs)
                except Interrupted as error:  # 中断异常，则不再重试
                    last_error = error
                    break_flag = True
                except Exception as error:  # pylint: disable=broad-exception-caught
                    last_error = error
                    if raise_exceptions:  # 遇到这些异常，则不再重试，其它都应该重试
                        if isinstance(error, raise_exceptions):
                            break_flag = True
                        else:
                            break_flag = False
                    else:  # 遇到这些异常，则重试，其它都不再重试
                        retry_exceptions = exceptions or Exception
                        if isinstance(error, retry_exceptions):
                            break_flag = False
                        else:
                            break_flag = True
                if break_flag is True:
                    raise last_error
                if sleep > 0:
                    time.sleep(sleep)
            raise last_error

        return functools.wraps(func)(wrapper)

    return outter_wrapper


class ChainableProxy(object):
    """Use in creating a server proxy.

    class ServerProxy(object):

        def __getattr__(self, name):
            return ChainableProxy(name, self._proxy_callback)

        def _proxy_callback(self, path, *args, **kwargs):
            return self.remote_exeucte(path, *args, **kwargs)

    server = ServerProxy(...)
    server.debug.ping()
    server.myapp.my_remote_call(...)
    """

    def __init__(self, path, proxy_callback, proxy_callback_extra_data=None):
        self.path = path
        self.proxy_callback = proxy_callback
        self.proxy_callback_extra_data = proxy_callback_extra_data or {}

    def __getattr__(self, name):
        return ChainableProxy(
            ".".join([self.path, name]),
            self.proxy_callback,
            self.proxy_callback_extra_data,
        )

    def __call__(self, *args, **kwargs):
        args = args or tuple([])
        args = tuple([self.path]) + args
        kwargs = kwargs or {}
        for key, value in self.proxy_callback_extra_data.items():
            kwargs.setdefault(key, value)
        return self.proxy_callback(*args, **kwargs)


### alias to keep old compatiable
is_a_class = isclass


def get_method_help(func):
    """
    获取函数的帮助信息。一般用于rpc提示。
    """
    if hasattr(func, "__help_text__"):
        return getattr(func, "__help_text__")
    if hasattr(func, "__help__"):
        return getattr(func, "__help__")
    if hasattr(func, "__doc__"):
        return getattr(func, "__doc__")
    return ""


def get_method_signature(func):
    """
    获取函数的参数和返回值信息。一般用于rpc提示。
    """
    if hasattr(func, "__signature__"):
        return getattr(func, "__signature__")
    help_text = get_method_help(func)
    if help_text:
        sigs = [
            x.strip()
            for x in re.findall(
                "@signature \\{\\{\\{(.*)\\}\\}\\}",
                help_text,
                re.MULTILINE | re.IGNORECASE | re.DOTALL,
            )
        ]
        if sigs:
            return json.loads(sigs[0])
    return []
