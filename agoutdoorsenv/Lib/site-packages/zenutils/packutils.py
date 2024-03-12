#!/usr/bin/env python
# -*- coding: utf8 -*-
"""数据封装工具。"""
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
    "AbstractResultPacker",
    "RcmPacker",
]

from zenutils.errorutils import OK
from zenutils.errorutils import BizError
from zenutils.errorutils import InformalResultPackage


class AbstractResultPacker(object):
    """第1个位置参数加入了后缀，避免与kwargs中的参数冲突。"""

    def pack_result(self, _result_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        raise NotImplementedError()

    def pack_error(self, _error_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        raise NotImplementedError()

    def unpack(self, _data_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        raise NotImplementedError()


class RcmPacker(AbstractResultPacker):
    ok = OK()

    def pack_result(self, _result_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        return {
            "result": _result_Pu1dvy86uRLpdNu2Czyf,
            "code": self.ok.code,
            "message": self.ok.message,
        }

    def pack_error(
        self, _error_Pu1dvy86uRLpdNu2Czyf, _result_Pu1dvy86uRLpdNu2Czyf=None, **kwargs
    ):
        error = BizError(_error_Pu1dvy86uRLpdNu2Czyf)
        return {
            "result": _result_Pu1dvy86uRLpdNu2Czyf,
            "code": error.code,
            "message": error.message,
        }

    def unpack(self, _data_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        if not "code" in _data_Pu1dvy86uRLpdNu2Czyf:
            raise InformalResultPackage(1211060001, "missing field: code")

        if not _data_Pu1dvy86uRLpdNu2Czyf["code"]:
            if not "result" in _data_Pu1dvy86uRLpdNu2Czyf:
                raise InformalResultPackage(1211060001, "missing field: result")
            else:
                return _data_Pu1dvy86uRLpdNu2Czyf["result"]
        else:
            if not "message" in _data_Pu1dvy86uRLpdNu2Czyf:
                raise InformalResultPackage(1211060001, "missing field: message")
            else:
                raise BizError(
                    message=_data_Pu1dvy86uRLpdNu2Czyf["message"],
                    code=_data_Pu1dvy86uRLpdNu2Czyf["code"],
                )
