#!/usr/bin/env python
# -*- coding: utf8 -*-
"""网络服务实现辅助工具。"""
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
    "ServerEngineBase",
    "NStreamExchangeProtocolBase",
    "ServerHandle",
]

import struct
import logging

from zenutils import dictutils
from zenutils import errorutils
from zenutils import importutils

_logger = logging.getLogger(__name__)


class ServerEngineBase(object):
    def __init__(self, config):
        self.config = dictutils.Object(config or {})
        self._services = (
            {}
        )  # hold all registered services, categoried by service namespace.
        self._shutdown = False
        self.core_server = self.make_core_server()

    def serve_forever(self):
        self._shutdown = False
        return self.core_server.serve_forever()

    def shutdown(self):
        self._shutdown = True
        self.stop_core_server()

    def stop_core_server(self):
        self.core_server.shutdown()

    def register_function(self, method, name):
        _logger.debug(
            "Registering method {name}: {method}".format(name=name, method=method)
        )
        self._services[name] = method

    def get_service(self, name):
        return self._services.get(name, None)

    def make_core_server(self):
        raise NotImplementedError()


class NStreamExchangeProtocolBase(object):
    """
    server.max_request_size: 2**20*4
    server.buffer_size: 4096
    server.rfile_buffer_size: server.buffer_size
    server.wfile_buffer_size: server.buffer_size
    server.exchange_protocol: None
    """

    package_size_bytes = 4
    package_size_struct_pack_sign = ">I"

    def __init__(self, server_engine, config, client_socket, client_address):
        self.server_engine = server_engine
        self.config = config
        self.client_socket = client_socket
        self.client_address = client_address
        self.setup()

    def setup(self):
        self.max_request_size = self.config.select(
            "server.max_request_size", 2**20 * 4
        )  # default to 4M
        self.buffer_size = self.config.select("server.buffer_size", 4096)
        self.rfile_buffer_size = self.config.select(
            "server.rfile_buffer_size", self.buffer_size
        )
        self.wfile_buffer_size = self.config.select(
            "server.wfile_buffer_size", self.buffer_size
        )
        self.rfile = self.client_socket.makefile(
            "rb", self.rfile_buffer_size
        )  # the second parameter named buffering in new version python, bug named bufsize in old version python
        self.wfile = self.client_socket.makefile(
            "wb", self.wfile_buffer_size
        )  # so we just using positional parameters here...

    def handle(self):
        try:
            while True:
                request = self.get_request()
                response = self.dispatch(request)
                self.send_response(response)
        except errorutils.ClientLostError as error:
            _logger.info(
                "socket server process info: client_address={address}, info=connection closed by client.".format(
                    address=self.client_address
                )
            )
        except Exception as error:
            error = errorutils.BizError(error)
            _logger.exception(
                "socket server process error: client_address={address}, error_code={code}, error_message={message}...".format(
                    address=self.client_address, code=error.code, message=error.message
                )
            )
        finally:
            try:
                self.client_socket.close()
                _logger.info(
                    "socket server process info: client_address={address}, info=connection closed by server.".format(
                        address=self.client_address
                    )
                )
            except Exception as error:
                _logger.info(
                    "socket server process error: client_address={address}, error_message=close client socket failed, system_error_message={error}...".format(
                        address=self.client_address, error=error
                    )
                )

    def dispatch(self, request):
        raise NotImplementedError()

    def get_request_size(self):
        size_bytes = self.rfile.read(self.package_size_bytes)
        if not size_bytes:
            raise errorutils.ClientLostError()
        size = struct.unpack(self.package_size_struct_pack_sign, size_bytes)[0]
        if size > self.max_request_size:
            raise errorutils.TooLargeRequestError(
                size=size, maxsize=self.max_request_size
            )
        return size

    def get_request(self):
        request_size = self.get_request_size()
        if not request_size:  # empty request
            return None
        request_bytes = self.rfile.read(request_size)
        if not request_bytes:
            raise errorutils.ClientLostError()
        return request_bytes

    def send_response(self, response_bytes):
        response_size = len(response_bytes)
        response_size_bytes = struct.pack(
            self.package_size_struct_pack_sign, response_size
        )
        self.wfile.write(response_size_bytes)
        self.wfile.write(response_bytes)
        self.wfile.flush()


class ServerHandle(object):
    def __init__(self, server_engine, config, exchange_protocol_class=None):
        self.server_engine = server_engine
        self.config = config
        if exchange_protocol_class:
            self.exchange_protocol_class = exchange_protocol_class
        else:
            exchange_protocol_class_name = self.config.select(
                "server.exchange_protocol", None
            )
            if not exchange_protocol_class_name:
                _logger.fatal("Config item server.exchange_protocol is missing...")
                raise errorutils.MissingConfigItem(item="server.exchange_protocol")
            self.exchange_protocol_class = importutils.import_from_string(
                exchange_protocol_class_name
            )

    def __call__(self, socket, address):
        protocol = self.exchange_protocol_class(
            self.server_engine, self.config, socket, address
        )
        protocol.handle()
