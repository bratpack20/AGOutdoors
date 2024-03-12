#!/usr/bin/env python
# -*- coding: utf8 -*-
"""服务实现辅助工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
from zenutils.sixutils import *

__all__ = [
    "ServiceBase",
    "DebugService",
]

import os
import time
import uuid
import platform

from zenutils.baseutils import Null
from zenutils.dictutils import Object


class UnsupportedService(RuntimeError):
    def __init__(self):
        super().__init__(1001120002, "不受支持的服务请求")


class ServerBase(object):
    def __init__(self):
        self.services = {}

    def register_function(self, method, name):
        self.services[name] = method

    def dispatch(self, name, args=None, kwargs=None):
        args = args or ()
        kwargs = kwargs or {}
        method = self.services.get(name, None)
        if method is None:
            raise UnsupportedService()
        return method(*args, **kwargs)


class ServiceBase(object):
    """Service base class.

    A service must be register to a server. A server must provides a register_function.

    class ServerBase(object):

        def register_function(self, method, name):
            pass

    """

    def __init__(self, config=None, namespace=None):
        """
        @param config: Dict like object. Suggest to use dictutils.Object type.
        @param namespace: Use empty string to force an empty namespace.
        """
        self.config = Object(config or {})
        if not namespace is None:
            self.namespace = namespace
        self.__setup__()

    def __setup__(self):
        pass

    def get_ignore_methods(self):
        """All public methods will be registered as a service except you add the method's name here."""
        return [
            "get_ignore_methods",
            "register_to",
            "get_server_service",
            "get_namespace",
            "get_methods",
        ]

    def register_to(self, server):
        # service instance can only be registered once
        if hasattr(self, "_server"):
            raise Exception("service is already registered...")
        self._server = server
        # register all methods to the server
        for name, method in self.get_methods():
            self._server.register_function(method, name)
        # keep service instance in server._services
        # service._services[""] will holds all non-namespace services
        if not hasattr(self._server, "_services"):
            setattr(self._server, "_services", {})
        services = getattr(self._server, "_services")
        namespace = self.get_namespace()
        if namespace:
            services[namespace] = self
        else:
            if not "" in services:
                services[""] = []
            services[""].append(self)
        # register done

    def get_server_service(self, name):
        if not self._server:
            raise Exception("service is not register to any server...")
        if not hasattr(self._server, "_services"):
            setattr(self._server, "_services", {})
        return self._server._services.get(name, None)

    def get_namespace(self):
        namespace = getattr(self, "namespace", Null)
        if namespace is Null:
            namespace = str(self.__class__.__name__).lower()
            if namespace.endswith("service"):
                namespace = namespace[:-7]
        return namespace

    def get_methods(self):
        methods = []
        ignore_names = self.get_ignore_methods()
        namespace = self.get_namespace()
        for name in dir(self):
            if name in ignore_names:
                continue
            method = getattr(self, name)
            if not name.startswith("_") and callable(method):
                if namespace:
                    name = self.get_namespace() + "." + name
                methods.append((name, method))
        return methods


class DebugService(ServiceBase):
    namespace = "debug"

    def __setup__(self):
        self._counter = 0

    def ping(self):
        """returns "pong" response.

        @methodSignature: ["str"]
        """
        return "pong"

    def echo(self, msg):
        """returns the content of the input.

        @signature: ["str", "str"]
        """
        return msg

    def timestamp(self):
        """returns server timestamp.

        @signature: ["float"]
        """
        return time.time()

    def hostname(self):
        """returns server hostname."""
        return platform.node()

    hostname._methodSignature = ["str"]

    def uuid4(self):
        """returns an UUID string."""
        return str(uuid.uuid4())

    uuid4._signature = ("str",)

    def urandom(self, length=32):
        """returns a random string.

        @signature: ["str", "int"]
        """
        return os.urandom(length)

    def uname(self):
        """returns server uname information.

        @returns: dict
        @args: []
        """
        info = platform.uname()
        uname = {}
        for name in dir(info):
            if name.startswith("_"):
                continue
            value = getattr(info, name)
            if callable(value):
                continue
            uname[name] = value
        return uname

    def true(self):
        """returns True value."""
        return True

    true._returns = "bool"
    true._args = []

    def false(self):
        """returns False value."""
        return False

    false._returns = "bool"
    false._args = ()

    def null(self):
        """returns None value.

        @signature: ["null"]
        """
        return None

    def sum(self, a, b, c=None):
        """do math sum to all inputs.

        @methodSignature: ["int", "int", "int"]
        @methodSignature: ["int", "int", "int", "int"]
        """
        if c is None:
            return sum([a, b])
        else:
            return sum([a, b, c])

    def counter(self):
        """returns the counter value starts from 1.

        @signature: ["int"]
        """
        self._counter += 1
        return self._counter

    def sleep(self, seconds=30.0):
        """sleep 30 seconds and then returns True value.

        @signature: ["bool", "float"]
        """
        time.sleep(seconds)
        return True

    def raise_error(self):
        """Always raise ZeroDivisionError."""
        a = 0
        b = 0
        c = a / b
        return c


class SimpleServer(ServerBase):
    pass
