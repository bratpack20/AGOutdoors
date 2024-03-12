#!/usr/bin/env python
# -*- coding: utf8 -*-
"""异常类工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
import json

__all__ = [
    "clean_language_name",
    "set_language",
    "get_language",
    "set_error_info",
    "get_error_info",
    "BizErrorBase",
    "OK",
    "BizError",
    "InformalResultPackage",
    "SYSTEM_ERROR_CODE_MAPPING",
    "SysError",
    "UndefinedError",
    "DatabaseError",
    "CacheError",
    "MessageQueueError",
    "AnotherServiceError",
    "HttpError",
    "RequestExpired",
    "NotSupportedHttpMethod",
    "BadResponseContent",
    "NoMatchingRouteFound",
    "ReqeustForbidden",
    "NoUpstreamServerAvailabe",
    "ConfigError",
    "MissingConfigItem",
    "DataError",
    "TargetNotFound",
    "AuthError",
    "AccountLockedError",
    "AccountTemporaryLockedError",
    "UserPasswordError",
    "AppAuthFailed",
    "TsExpiredError",
    "AccountDisabledError",
    "AccountStatusError",
    "AccountRemovedError",
    "LoginRequired",
    "AccessDenied",
    "UserDoesNotExist",
    "BadUserToken",
    "ReqidDuplicateError",
    "TypeError",
    "ParseJsonError",
    "InformalResultPackage",
    "InformalRequestError",
    "TooLargeRequestError",
    "ParamError",
    "MissingParameter",
    "BadParameter",
    "BadParameterType",
    "StringTooShort",
    "StringTooLong",
    "MissingField",
    "WrongFieldType",
    "WrongParameterType",
    "ValueExceedsMaxLimit",
    "ValueLessThanMinLimit",
    "FormError",
    "CaptchaOnlyAllowedOnce",
    "CaptchaValidateFailed",
    "RepeatedlySubmitForm",
    "CaptchaRequired",
    "LogicError",
    "CastFailedError",
    "CastToIntegerFailed",
    "CastToFloatFailed",
    "CastToNumbericFailed",
    "CastToBooleanFailed",
    "CastToStringFailed",
    "NotSupportedTypeToCast",
    "PermissionError",
    "NoPermissionError",
    "NoReadPermissionError",
    "NoWritePermissionError",
    "NoDeletePermissionError",
    "NoAccessPermissionError",
    "NoPermissionToCleanCacheError",
    "NetworkError",
    "ClientLostError",
    "ServiceError",
    "EventNotRegistered",
]

LANGUAGE = "zh-hans"

ERROR_INFO = {"en": {}, "zh-hans": {}}


def clean_language_name(language):
    if language is None:
        return LANGUAGE
    else:
        return language.lower().strip().replace("_", "-")


def set_language(language):
    global LANGUAGE
    language = clean_language_name(language)
    LANGUAGE = language


def get_language():
    return LANGUAGE


def set_error_info(language, class_name, code, message):
    language = clean_language_name(language)
    if not language in ERROR_INFO:
        ERROR_INFO[language] = {}
    ERROR_INFO[language][class_name] = {
        "code": code,
        "message": message,
    }


def get_error_info(class_name, language=None):
    language = clean_language_name(language)
    return ERROR_INFO[language].get(class_name, None)


class BizErrorBase(RuntimeError):
    """Base class of all errors."""

    def __init__(self, message=None, code=None, **kwargs):
        from . import strutils

        if isinstance(
            message, BizErrorBase
        ):  # 从BizErrorBase构造新的BizError，直接复制其code和message
            code = code or message.code
            message = message.message
        elif isinstance(
            message, dict
        ):  # 从{code: xx, message: xxx}字典构造新的BizError，直接复制期code/message字段值
            code = code or message.get("code", -1)
            message = message.get("message", message)
        elif isinstance(
            message, Exception
        ):  # 从python内置异常类构造新的BizError，根据系统内置code映射表设置code
            error = message
            code = 0
            message = None
            if len(error.args) >= 2:  # 如果内置异常遵循(code, message)参数形式构建，则尝试提取其code和message
                try:
                    code = int(error.args[0])
                    message = error.args[1:]
                    if len(message) == 1:
                        message = message[0]
                    else:
                        message = " ".join([strutils.force_text(x) for x in message])
                except Exception:
                    code = 0
                    message = None
            if not code:  # 尝试从自定义错误列表中提取code和message
                info = get_error_info(error.__class__.__name__)
                if info:
                    code = info["code"]
                    if (
                        len(error.args) == 1
                    ):  # 不要直接使用repr，直接使用repr会导致将异常实例RuntimeError("error reason")转成"RuntimeError"字符串，而非"error reason"字符串
                        message = error.args[0]
                    elif len(error.args) > 1:
                        message = " ".join([strutils.force_text(x) for x in error.args])
                    else:
                        message = info["message"]
            if not code:  # 如果提取失败，则根据异常类名提取code
                code = SYSTEM_ERROR_CODE_MAPPING.get(error.__class__.__name__, 0)
                if code:
                    if (
                        len(error.args) == 1
                    ):  # 不要直接使用repr，直接使用repr会导致将异常实例RuntimeError("error reason")转成"RuntimeError"字符串，而非"error reason"字符串
                        message = error.args[0]
                    elif len(error.args) > 1:
                        message = " ".join([strutils.force_text(x) for x in error.args])
                    else:
                        message = error.__class__.__name__
        else:
            # load default code & message
            info = get_error_info(self.__class__.__name__)
            code = code or info["code"]
            message = message or info["message"]
        message = strutils.force_text(message)
        if kwargs:
            message = message.format(**kwargs)
        super(BizErrorBase, self).__init__(code, message)

    def __repr__(self):
        from . import sixutils
        from . import strutils

        result = json.dumps(
            {"code": self.args[0], "message": self.args[1]}, ensure_ascii=False
        )
        if sixutils.PY2:
            return strutils.force_bytes(result)
        else:
            return strutils.force_text(result)

    def __str__(self):
        from . import sixutils
        from . import strutils

        result = json.dumps(
            {"code": self.args[0], "message": self.args[1]}, ensure_ascii=False
        )
        if sixutils.PY2:
            return strutils.force_bytes(result)
        else:
            return strutils.force_text(result)

    def __unicode__(self):
        from . import strutils

        result = json.dumps(
            {"code": self.args[0], "message": self.args[1]}, ensure_ascii=False
        )
        return strutils.force_text(result)

    def update(self, **kwargs):
        self.args = (self.args[0], self.args[1].format(**kwargs))

    @property
    def code(self):
        return self.args[0]

    @property
    def message(self):
        return self.args[1]

    @property
    def json(self):
        return {
            "code": self.code,
            "message": self.message,
        }


class OK(BizErrorBase):
    pass


set_error_info("en", "OK", 0, "OK")
set_error_info("zh-hans", "OK", 0, "正常。")


class BizError(BizErrorBase):
    pass


set_error_info("en", "BizError", 1, "Error")
set_error_info("zh-hans", "BizError", 1, "异常！")


SYSTEM_ERROR_CODE_MAPPING = {
    "ArithmeticError": 102,
    "AssertionError": 104,
    "AttributeError": 106,
    "BaseException": 108,
    "BlockingIOError": 110,
    "BrokenPipeError": 112,
    "BufferError": 114,
    "BytesWarning": 116,
    "ChildProcessError": 118,
    "ConnectionAbortedError": 120,
    "ConnectionError": 122,
    "ConnectionRefusedError": 124,
    "ConnectionResetError": 126,
    "DeprecationWarning": 128,
    "EOFError": 130,
    "EncodingWarning": 132,
    "Exception": 134,
    "FileExistsError": 136,
    "FileNotFoundError": 138,
    "FloatingPointError": 140,
    "FutureWarning": 142,
    "GeneratorExit": 144,
    "ImportError": 146,
    "ImportWarning": 148,
    "IndentationError": 150,
    "IndexError": 152,
    "InterruptedError": 154,
    "IsADirectoryError": 156,
    "KeyError": 158,
    "KeyboardInterrupt": 160,
    "LookupError": 162,
    "MemoryError": 164,
    "ModuleNotFoundError": 166,
    "NameError": 168,
    "NotADirectoryError": 170,
    "NotImplementedError": 172,
    "OSError": 174,
    "OverflowError": 176,
    "PendingDeprecationWarning": 178,
    "PermissionError": 180,
    "ProcessLookupError": 182,
    "RecursionError": 184,
    "ReferenceError": 186,
    "ResourceWarning": 188,
    "RuntimeError": 190,
    "RuntimeWarning": 192,
    "StopAsyncIteration": 194,
    "StopIteration": 196,
    "SyntaxError": 198,
    "SyntaxWarning": 200,
    "SystemError": 202,
    "SystemExit": 204,
    "TabError": 206,
    "TimeoutError": 208,
    "TypeError": 210,
    "UnboundLocalError": 212,
    "UnicodeDecodeError": 214,
    "UnicodeEncodeError": 216,
    "UnicodeError": 218,
    "UnicodeTranslateError": 220,
    "UnicodeWarning": 222,
    "UserWarning": 224,
    "ValueError": 226,
    "Warning": 228,
    "ZeroDivisionError": 230,
}


class SysError(BizErrorBase):
    pass


set_error_info("en", "SysError", 1001000000, "System Error")
set_error_info("zh-hans", "SysError", 1001000000, "系统异常！")


class UndefinedError(SysError):
    pass


set_error_info("en", "UndefinedError", 1001000001, "Undefined Error")
set_error_info("zh-hans", "UndefinedError", 1001000001, "未定义的异常！")


class DatabaseError(SysError):
    pass


set_error_info("en", "DatabaseError", 1001000002, "System Error")
set_error_info("zh-hans", "DatabaseError", 1001000002, "数据库异常！")


class CacheError(SysError):
    pass


set_error_info("en", "CacheError", 1001000003, "System Error")
set_error_info("zh-hans", "CacheError", 1001000003, "缓存异常！")


class MessageQueueError(SysError):
    pass


set_error_info("en", "MessageQueueError", 1001000004, "System Error")
set_error_info("zh-hans", "MessageQueueError", 1001000004, "消息队列异常！")


class AnotherServiceError(SysError):
    pass


set_error_info("en", "AnotherServiceError", 1001000005, "System Error")
set_error_info("zh-hans", "AnotherServiceError", 1001000005, "外部服务异常！")


class HttpError(BizErrorBase):
    pass


set_error_info("en", "HttpError", 1001010000, "Http Error.")
set_error_info("zh-hans", "HttpError", 1001010000, "HTTP请求相关异常。")


class RequestExpired(HttpError):
    pass


set_error_info("en", "RequestExpired", 1001010001, "Request expired.")
set_error_info("zh-hans", "RequestExpired", 1001010001, "请求已过期！")


class NotSupportedHttpMethod(HttpError):
    pass


set_error_info("en", "NotSupportedHttpMethod", 1001010002, "Not supported http method.")
set_error_info("zh-hans", "NotSupportedHttpMethod", 1001010002, "不支持的请求方法！")


class BadResponseContent(HttpError):
    pass


set_error_info(
    "en",
    "BadResponseContent",
    1001010003,
    "Bad response content. Content returned: {content}.",
)
set_error_info(
    "zh-hans", "BadResponseContent", 1001010003, "HTTP接口响应内容格式非法，响应报文内容为{content}。"
)


class NoMatchingRouteFound(HttpError):
    pass


set_error_info("en", "NoMatchingRouteFound", 1001010004, "No matching route found.")
set_error_info("zh-hans", "NoMatchingRouteFound", 1001010004, "未找到匹配的路由！")


class ReqeustForbidden(HttpError):
    pass


set_error_info("en", "ReqeustForbidden", 1001010005, "Request forbidden.")
set_error_info("zh-hans", "ReqeustForbidden", 1001010005, "拒绝访问！")


class NoUpstreamServerAvailabe(HttpError):
    pass


set_error_info(
    "en", "NoUpstreamServerAvailabe", 1001010006, "No upstream server availabe."
)
set_error_info("zh-hans", "NoUpstreamServerAvailabe", 1001010006, "没有找到有效的后端服务节点！")


class ConfigError(BizErrorBase):
    pass


set_error_info("en", "ConfigError", 1001020000, "Config error.")
set_error_info("zh-hans", "ConfigError", 1001020000, "配置相关异常。")


class MissingConfigItem(ConfigError):
    pass


set_error_info("en", "MissingConfigItem", 1001020001, "Missing config item: {item}.")
set_error_info("zh-hans", "MissingConfigItem", 1001020001, "缺少必要的配置项：{item}。")


class DataError(BizErrorBase):
    pass


set_error_info("en", "DataError", 1001030000, "Data error.")
set_error_info("zh-hans", "DataError", 1001030000, "数据相关异常。")


class TargetNotFound(DataError):
    pass


set_error_info("en", "TargetNotFound", 1001030001, "Target not found.")
set_error_info("zh-hans", "TargetNotFound", 1001030001, "没有找到目标对象！")


class AuthError(BizErrorBase):
    pass


set_error_info("en", "AuthError", 1001040000, "Auth error.")
set_error_info("zh-hans", "AuthError", 1001040000, "认证相关异常。")


class AccountLockedError(AuthError):
    pass


set_error_info("en", "AccountLockedError", 1001040001, "Account locked.")
set_error_info("zh-hans", "AccountLockedError", 1001040001, "帐号被锁定，请联系管理员！")


class AccountTemporaryLockedError(AuthError):
    pass


set_error_info(
    "en", "AccountTemporaryLockedError", 1001040002, "Account temporary locked."
)
set_error_info(
    "zh-hans", "AccountTemporaryLockedError", 1001040002, "登录失败次数超过上限，帐号被临时锁定！"
)


class UserPasswordError(AuthError):
    pass


set_error_info(
    "en", "UserPasswordError", 1001040003, "User not exist or wrong password."
)
set_error_info("zh-hans", "UserPasswordError", 1001040003, "帐号或密码错误，请重试！")


class AppAuthFailed(AuthError):
    pass


set_error_info("en", "AppAuthFailed", 1001040004, "App auth failed.")
set_error_info("zh-hans", "AppAuthFailed", 1001040004, "应用认证失败！")


class TsExpiredError(AuthError):
    pass


set_error_info("en", "TsExpiredError", 1001040005, "Timestamp expired.")
set_error_info("zh-hans", "TsExpiredError", 1001040005, "时间戳已失效。")


class AccountDisabledError(AuthError):
    pass


set_error_info("en", "AccountDisabledError", 1001040006, "Account disabled.")
set_error_info("zh-hans", "AccountDisabledError", 1001040006, "帐号已禁用，请联系管理员！")


class AccountStatusError(AuthError):
    pass


set_error_info("en", "AccountStatusError", 1001040007, "Bad account status.")
set_error_info("zh-hans", "AccountStatusError", 1001040007, "帐号状态异常，请联系管理员处理！")


class AccountRemovedError(AuthError):
    pass


set_error_info("en", "AccountRemovedError", 1001040008, "Account removed.")
set_error_info("zh-hans", "AccountRemovedError", 1001040008, "帐号已删除！")


class LoginRequired(AuthError):
    pass


set_error_info("en", "LoginRequired", 1001040009, "Login required.")
set_error_info("zh-hans", "LoginRequired", 1001040009, "请先登录！")


class AccessDenied(AuthError):
    pass


set_error_info("en", "AccessDenied", 1001040010, "Access denied.")
set_error_info("zh-hans", "AccessDenied", 1001040010, "禁止访问！")


class UserDoesNotExist(AuthError):
    pass


set_error_info("en", "UserDoesNotExist", 1001040011, "User does not exist.")
set_error_info("zh-hans", "UserDoesNotExist", 1001040011, "帐号不存在！")


class BadUserToken(AuthError):
    pass


set_error_info("en", "BadUserToken", 1001040012, "Bad user token.")
set_error_info("zh-hans", "BadUserToken", 1001040012, "用户令牌无效！")


class ReqidDuplicateError(AuthError):
    pass


set_error_info("en", "ReqidDuplicateError", 1001040013, "Reqid duplicate error.")
set_error_info("zh-hans", "ReqidDuplicateError", 1001040013, "请求流水号重复!")


class AuthenticationRequired(AuthError):
    pass


set_error_info("en", "AuthenticationRequired", 1001040014, "Authentication required.")
set_error_info("zh-hans", "AuthenticationRequired", 1001040014, "请先完成身份认证才能使用本服务！")


class TypeError(BizErrorBase):
    pass


set_error_info("en", "TypeError", 1001050000, "Type error.")
set_error_info("zh-hans", "TypeError", 1001050000, "数据类型相关异常。")


class ParseJsonError(TypeError):
    pass


set_error_info("en", "ParseJsonError", 1001050006, "Parse json error. Raw text {text}.")
set_error_info(
    "zh-hans", "ParseJsonError", 1001050006, "字段{field}值为{value}{text}进行Json反序列化异常！"
)


class InformalResultPackage(TypeError):
    pass


set_error_info(
    "en", "InformalResultPackage", 1001050007, "Informal result package: {message}."
)
set_error_info("zh-hans", "InformalResultPackage", 1001050007, "错误的数据封装包：{message}。")


class InformalRequestError(TypeError):
    pass


set_error_info(
    "en", "InformalRequestError", 1001050008, "Informal request error: {message}."
)
set_error_info("zh-hans", "InformalRequestError", 1001050008, "请求体格式错误：{message}。")


class TooLargeRequestError(TypeError):
    pass


set_error_info(
    "en",
    "TooLargeRequestError",
    1001050009,
    "Too large request error: {size} > {maxsize}.",
)
set_error_info(
    "zh-hans", "TooLargeRequestError", 1001050009, "请求体过大：{size} > {maxsize}。"
)


class ParamError(BizErrorBase):
    pass


set_error_info("en", "ParamError", 1001060000, "Param error.")
set_error_info("zh-hans", "ParamError", 1001060000, "参数相关异常。")


class MissingParameter(ParamError):
    pass


set_error_info("en", "MissingParameter", 1001060001, "Missing parameter: {parameter}.")
set_error_info("zh-hans", "MissingParameter", 1001060001, "必要参数缺失：{parameter}。")


class BadParameter(ParamError):
    pass


set_error_info("en", "BadParameter", 1001060002, "Bad parameter: {parameter}.")
set_error_info("zh-hans", "BadParameter", 1001060002, "参数值有误：{parameter}。")


class BadParameterType(ParamError):
    pass


set_error_info("en", "BadParameterType", 1001060003, "Bad parameter type: {parameter}.")
set_error_info("zh-hans", "BadParameterType", 1001060003, "参数类型有误：{parameter}。")


class StringTooShort(ParamError):
    pass


set_error_info("en", "StringTooShort", 1001060004, "String shorter than {min_length}.")
set_error_info("zh-hans", "StringTooShort", 1001060004, "参数字符数不足，最低要求为：{min_length}。")


class StringTooLong(ParamError):
    pass


set_error_info("en", "StringTooLong", 1001060005, "String longer than {max_length}.")
set_error_info("zh-hans", "StringTooLong", 1001060005, "参数字符数过多，最高限定为：{max_length}。")


class MissingField(ParamError):
    pass


set_error_info("en", "MissingField", 1001060006, "Missing field: {field}.")
set_error_info("zh-hans", "MissingField", 1001060006, "字段缺失：{field}。")


class WrongFieldType(ParamError):
    pass


set_error_info("en", "WrongFieldType", 1001060007, "Wrong field type.")
set_error_info("zh-hans", "WrongFieldType", 1001060007, "字段类型不匹配！")


class WrongParameterType(ParamError):
    pass


set_error_info("en", "WrongParameterType", 1001060008, "Wrong parameter type.")
set_error_info("zh-hans", "WrongParameterType", 1001060008, "参数类型不匹配！")


class ValueExceedsMaxLimit(ParamError):
    pass


set_error_info(
    "en", "ValueExceedsMaxLimit", 1001060009, "The value exceeds the upper limit."
)
set_error_info("zh-hans", "ValueExceedsMaxLimit", 1001060009, "数值{value}超过最大限制{max}！")


class ValueLessThanMinLimit(ParamError):
    pass


set_error_info(
    "en",
    "ValueLessThanMinLimit",
    1001060010,
    "The value is less than the minimum limit.",
)
set_error_info("zh-hans", "ValueLessThanMinLimit", 1001060010, "数值{value}小于最小限制{min}！")


class FormError(BizErrorBase):
    pass


set_error_info("en", "FormError", 1001070000, "Form error.")
set_error_info("zh-hans", "FormError", 1001070000, "表单相关异常。")


class CaptchaOnlyAllowedOnce(FormError):
    pass


set_error_info(
    "en", "CaptchaOnlyAllowedOnce", 1001070001, "Captcha only allowed one time use."
)
set_error_info("zh-hans", "CaptchaOnlyAllowedOnce", 1001070001, "验证码不允许重复使用！")


class CaptchaValidateFailed(FormError):
    pass


set_error_info("en", "CaptchaValidateFailed", 1001070002, "Captcha validate failed.")
set_error_info("zh-hans", "CaptchaValidateFailed", 1001070002, "图形验证码校验失败，请输入正确的图形验证码！")


class RepeatedlySubmitForm(FormError):
    pass


set_error_info(
    "en", "RepeatedlySubmitForm", 1001070003, "Please do not submit a form repeatedly."
)
set_error_info("zh-hans", "RepeatedlySubmitForm", 1001070003, "请不要重复提交表单！")


class CaptchaRequired(FormError):
    pass


set_error_info("en", "CaptchaRequired", 1001070004, "Captcha Required.")
set_error_info("zh-hans", "CaptchaRequired", 1001070004, "启用图形验证码校验，请输入正确的验证码。")


class LogicError(BizErrorBase):
    pass


set_error_info("en", "LogicError", 1001080000, "Logic error.")
set_error_info("zh-hans", "LogicError", 1001080000, "业务逻辑相关异常。")


class CastFailedError(BizErrorBase):
    pass


set_error_info("en", "CastFailedError", 1001090000, "Type cast failed.")
set_error_info("zh-hans", "CastFailedError", 1001090000, "类型转化错误。")


class CastToIntegerFailed(CastFailedError):
    pass


set_error_info(
    "en",
    "CastToIntegerFailed",
    1001090001,
    "Cast to integer value failed on field {field} value={value}.",
)
set_error_info(
    "zh-hans", "CastToIntegerFailed", 1001090001, "字段{field}值为{value}转化整数型数据失败！"
)


class CastToFloatFailed(CastFailedError):
    pass


set_error_info(
    "en",
    "CastToFloatFailed",
    1001090002,
    "Cast to float value failed on field {field} value={value}.",
)
set_error_info(
    "zh-hans", "CastToFloatFailed", 1001090002, "字段{field}值为{value}转化浮点数型数据失败！"
)


class CastToNumbericFailed(CastFailedError):
    pass


set_error_info(
    "en",
    "CastToNumbericFailed",
    1001090003,
    "Cast to numberic value failed on field {field} value={value}.",
)
set_error_info(
    "zh-hans", "CastToNumbericFailed", 1001090003, "字段{field}值为{value}转化数值型数据失败！"
)


class CastToBooleanFailed(CastFailedError):
    pass


set_error_info(
    "en",
    "CastToBooleanFailed",
    1001090004,
    "Cast to boolean value failed on field {field} value={value}.",
)
set_error_info(
    "zh-hans", "CastToBooleanFailed", 1001090004, "字段{field}值为{value}转化布尔型数据失败！"
)


class CastToStringFailed(CastFailedError):
    pass


set_error_info(
    "en",
    "CastToStringFailed",
    1001090005,
    "Cast to string value failed on field {field} value={value}.",
)
set_error_info(
    "zh-hans", "CastToStringFailed", 1001090005, "字段{field}值为{value}转化字符串型数据失败！"
)


class NotSupportedTypeToCast(CastFailedError):
    pass


set_error_info(
    "en",
    "NotSupportedTypeToCast",
    1001090006,
    "Not supported type to cast on field {field} value={value} type={type}.",
)
set_error_info(
    "zh-hans", "NotSupportedTypeToCast", 1001090006, "字段{field}值为{value}不支持转化为{type}类型！"
)


class PermissionError(BizErrorBase):
    pass


set_error_info("en", "PermissionError", 1001100000, "Permission error.")
set_error_info("zh-hans", "PermissionError", 1001100000, "权限错误。")


class NoPermissionError(PermissionError):
    pass


set_error_info("en", "NoPermissionError", 1001100001, "No permission error.")
set_error_info("zh-hans", "NoPermissionError", 1001100001, "无权限错误！")


class NoReadPermissionError(PermissionError):
    pass


set_error_info("en", "NoReadPermissionError", 1001100002, "No read permission error.")
set_error_info("zh-hans", "NoReadPermissionError", 1001100002, "没有读权限错误！")


class NoWritePermissionError(PermissionError):
    pass


set_error_info("en", "NoWritePermissionError", 1001100003, "No write permission error.")
set_error_info("zh-hans", "NoWritePermissionError", 1001100003, "没有写权限错误！")


class NoDeletePermissionError(PermissionError):
    pass


set_error_info(
    "en", "NoDeletePermissionError", 1001100004, "No delete permission error."
)
set_error_info("zh-hans", "NoDeletePermissionError", 1001100004, "没有删除权限错误！")


class NoAccessPermissionError(PermissionError):
    pass


set_error_info(
    "en", "NoAccessPermissionError", 1001100005, "No access permission error."
)
set_error_info("zh-hans", "NoAccessPermissionError", 1001100005, "没有访问权限错误！")


class NoPermissionToCleanCacheError(PermissionError):
    pass


set_error_info(
    "en",
    "NoPermissionToCleanCacheError",
    1001100006,
    "No permission to clean cache error.",
)
set_error_info("zh-hans", "NoPermissionToCleanCacheError", 1001100006, "没有权限清除缓存！")


class NetworkError(BizErrorBase):
    pass


set_error_info("en", "NetworkError", 1001110000, "Network error.")
set_error_info("zh-hans", "NetworkError", 1001110000, "网络异常！")


class ClientLostError(NetworkError):
    pass


set_error_info("en", "ClientLostError", 1001110001, "Client lost error.")
set_error_info("zh-hans", "ClientLostError", 1001110001, "客户端连接已关闭。")


class SendRequestToServerError(NetworkError):
    pass


set_error_info(
    "en", "SendRequestToServerError", 1001110002, "Send request to server error."
)
set_error_info("zh-hans", "SendRequestToServerError", 1001110002, "向服务器发送请求失败！")


class RecvServerResponseError(NetworkError):
    pass


set_error_info(
    "en", "RecvServerResponseError", 1001110003, "Recv server response error."
)
set_error_info("zh-hans", "RecvServerResponseError", 1001110003, "接收服务器响应失败！")


class ServerGoneAwayError(NetworkError):
    pass


set_error_info("en", "ServerGoneAwayError", 1001110004, "Server gone away.")
set_error_info("zh-hans", "ServerGoneAwayError", 1001110004, "服务器连接已关闭！")


class ServiceError(BizErrorBase):
    pass


set_error_info("en", "ServiceError", 1001120000, "Service error.")
set_error_info("zh-hans", "ServiceError", 1001120000, "服务异常！")


class EventNotRegistered(ServiceError):
    pass


set_error_info("en", "EventNotRegistered", 1001120001, "Event not registered: {event}.")
set_error_info("zh-hans", "EventNotRegistered", 1001120001, "未注册的事件：{event}。")
