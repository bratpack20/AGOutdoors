#!/usr/bin/env python
# -*- coding: utf8 -*-
"""字符串工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
import itertools
import string
import binascii
import math
import re
import uuid
from decimal import Decimal
from io import BytesIO
from io import open
from .sixutils import *


__all__ = [
    "StrUtils",
    "HEXLIFY_CHARS",
    "URLSAFEB64_CHARS",
    "BASE64_CHARS",
    "SHI",
    "BAI",
    "QIAN",
    "WAN",
    "YI",
    "default_encodings",
    "default_encoding",
    "default_random_string_choices",
    "default_cn_yuan",
    "simple_cn_yuan",
    "default_cn_digits",
    "default_cn_places",
    "default_cn_negative",
    "default_cn_float_places",
    "random_string",
    "char_force_to_int",
    "force_int",
    "force_float",
    "force_numberic",
    "wholestrip",
    "simplesplit",
    "split2",
    "split",
    "force_type_to",
    "str_composed_by",
    "is_str_composed_by_the_choices",
    "is_hex_digits",
    "join_lines",
    "is_urlsafeb64_decodable",
    "is_base64_decodable",
    "is_unhexlifiable",
    "text_display_length",
    "text_display_shorten",
    "smart_get_binary_data",
    "is_chinese_character",
    "binarify",
    "unbinarify",
    "substrings",
    "combinations2",
    "combinations",
    "captital_number",
    "clean",
    "do_clean",
    "camel",
    "no_mapping",
    "none_to_empty_string",
    "strip_string",
    "format_with_mapping",
    "default_quotes",
    "unquote",
    "is_uuid",
    "stringlist_append",
    "html_element_css_append",
    "remove_prefix",
    "remove_suffix",
    "encodable",
    "decodable",
    "chunk",
    "get_all_substrings",
    "reverse",
    "get_image_bytes",
    "get_base64image",
    "parse_base64image",
    # ---------------------
    "bytes2ints",
    "ints2bytes",
    "int2bytes",
]

HEXLIFY_CHARS = TEXT("0123456789abcdefABCDEF")
URLSAFEB64_CHARS = TEXT(
    "-0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz\r\n"
)
BASE64_CHARS = TEXT(
    "+/0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\r\n"
)

SHI = 10
BAI = SHI * 10
QIAN = BAI * 10
WAN = QIAN * 10
YI = WAN * WAN

default_encodings = ["utf8", "gb18030"]
default_encoding = "utf-8"
default_random_string_choices = TEXT(string.ascii_letters)
default_cn_yuan = TEXT("圆")
simple_cn_yuan = TEXT("元")
default_cn_digits = TEXT("零壹贰叁肆伍陆柒捌玖")
default_cn_places = TEXT("拾佰仟万亿")
default_cn_negative = TEXT("负")
default_cn_float_places = TEXT("角分厘毫丝忽微")


def char_force_to_int(char):
    if callable(char):
        char = char()
    if char is None:
        return None
    if isinstance(char, int):
        return char
    return ord(char)


def force_int(value):
    if callable(value):
        value = value()
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, Decimal):
        return int(value)
    value = force_text(value)
    if "." in value:
        return int(float(value))
    return int(value)


def force_float(value):
    if callable(value):
        value = value()
    if value is None:
        return None
    if isinstance(value, float):
        return value
    if isinstance(value, int):
        return float(value)
    if isinstance(value, Decimal):
        return float(value)
    value = force_text(value)
    return float(value)


def force_numberic(value):
    if callable(value):
        value = value()
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        return value
    if isinstance(value, BYTES_TYPE):
        value = value.decode(default_encoding)
    value = str(value)
    if "." in value:
        return float(value)
    else:
        return int(value)


def wholestrip(text):
    """Remove all white spaces in text. White spaces are ' \\t\\n\\r\\x0b\\x0c\\u3000'.

    Note:

    It's NOT only trim the left and right white characters,
    but also remove white characters in the middle of the text.
    """
    if text is None:
        return None
    for space in string.whitespace + "\u3000":
        text = text.replace(space, "")
    return text


def simplesplit(text, sep=None, maxsplit=None):
    """Simple split. Same as str.split(xxx). Make it behave the same both in py2 and py3.

    @Returns:
        (list of str, list fof bytes): Return a list of the words in the string, using sep as the delimiter string.

    @Parameters:
        text(str or bytes): The text to be splitted.
        sep(str or bytes):  The delimiter according which to split the string.
                            None (the default value) means split according to any whitespace,
                            and discard empty strings from the result.
        maxsplit(int):      Maximum number of splits to do.
                            -1 means no limit.
                            None means using system default which is -1.
    """
    sep = force_type_to(sep, text)
    if maxsplit:
        return text.split(sep, maxsplit)
    elif sep:
        return text.split(sep)
    else:
        return text.split()


def split2(text, seps=None):
    """Split string into two parts."""
    if text is None:
        return None
    if not seps:
        ss = simplesplit(text, maxsplit=1)
    else:
        if not isinstance(seps, (list, set, tuple)):
            seps = [seps]
        min_index = len(text)
        min_sep = None
        for sep in seps:
            try:
                index = text.index(sep)
                if index < min_index:
                    min_index = index
                    min_sep = sep
            except ValueError:
                pass
        ss = simplesplit(text, sep=min_sep, maxsplit=1)
    if len(ss) == 0:
        ss.append("")
    if len(ss) == 1:
        ss.append("")
    return ss


def split(text, seps, strip=False):
    """Split string with a list of sperators. seps is a list of string, all sep in the seps are treated as delimiter."""
    if not text:
        return []
    if not isinstance(seps, (list, set, tuple)):
        seps = [seps]
    results = [text]
    for sep in seps:
        row = []
        for value in results:
            row += simplesplit(value, sep=sep)
        results = row
    if strip:
        row = []
        for value in results:
            row.append(value.strip())
        results = row
    return results


def force_type_to(src, dst):
    """Change src's type to the type of the dst.

    @Returns:
        (str or bytes): If dst is in bytes type, turns src's type to types, and returns changed value.
                        If dst is in str type, turns src's type to str, and returns changed value.
                        If dst is in other types, just returns the src value.

    @Parameters:
        src(str or bytes): The src data.
        target(str or bytes): The dst data, which type will be copied.

    """
    if isinstance(dst, STR_TYPE):
        return force_text(src)
    elif isinstance(dst, BYTES_TYPE):
        return force_bytes(src)
    else:
        return src


def str_composed_by(text, choices):
    """Test if text is composed by chars in the choices.

    @Returns:
        (bool): If all char in text is also in choices, returns True.
                If one char in text is NOT in choices, returns False.

    @Parameters:
        text(str or bytes): The text to be tested.
        choices(str, bytes, list of str char, list of bytes char): The good char set.
    """
    text = force_type_to(text, choices)
    text_set = set(text)
    choices_set = set(choices)
    if text_set - choices_set:  # text has char not in choices, so just returns False
        return False
    else:
        return True


is_str_composed_by_the_choices = str_composed_by


def is_hex_digits(text):
    """Test if all chars in text is hex digits."""
    if not text:
        return False
    return str_composed_by(text, HEXLIFY_CHARS)


def join_lines(text):
    """Join multi-lines into single line."""
    empty = force_type_to("", text)
    return empty.join(text.splitlines())


def is_urlsafeb64_decodable(text):
    """Test if the text can be decoded by urlsafeb64 method."""
    text = wholestrip(text)
    if not text:
        return False
    if len(text) % 4 != 0:
        return False
    text = join_lines(text)
    return str_composed_by(text, URLSAFEB64_CHARS)


def is_base64_decodable(text):
    """Test  if the text can be decoded by base64 method."""
    text = wholestrip(text)
    if not text:
        return False
    if len(text) % 4 != 0:
        return False
    text = join_lines(text)
    return str_composed_by(text, BASE64_CHARS)


def is_unhexlifiable(text):
    """Test if the text can be decoded by unhexlify method."""
    text = wholestrip(text)
    if not text:
        return False
    if len(text) % 2 != 0:
        return False
    return str_composed_by(text, HEXLIFY_CHARS)


def text_display_length(text, unicode_display_length=2, encoding=None):
    """Get text display length."""
    text = force_text(text, encoding)
    length = 0
    for c in text:
        if ord(c) <= 128:
            length += 1
        else:
            length += unicode_display_length
    return length


def text_display_shorten(
    text, max_length, unicode_display_length=2, suffix="...", encoding=None
):
    """Shorten text to fix the max display length."""
    text = force_text(text, encoding)
    if max_length < len(suffix):
        max_length = len(suffix)
    tlen = text_display_length(text, unicode_display_length=unicode_display_length)
    if tlen <= max_length:
        return text
    result = ""
    tlen = 0
    max_length -= len(suffix)
    for c in text:
        if ord(c) <= 128:
            tlen += 1
        else:
            tlen += unicode_display_length
        if tlen < max_length:
            result += c
        elif tlen == max_length:
            result += c
            break
        else:
            break
    result += suffix
    return result


def smart_get_binary_data(text):
    """Smart get bytes form the given data.

    @Returns:
        (bytes): The parsed bytes data.

    @Paramters:
        text(text or bytes): If text is bytes typed, just returns it's value.
                             If text is str typed, try to parse it.
                             First try to unhexlify it.
                             Second try to do urlsafe_b64decode it.
                             Third try to do base64.decodebytes on it.
                             Forth try to encode it as utf8(default_encoding).
    """
    from zenutils import base64utils

    if isinstance(text, STR_TYPE):
        if is_unhexlifiable(text):
            text = force_bytes(text)
            return binascii.unhexlify(text)
        elif is_urlsafeb64_decodable(text):
            text = force_bytes(text)
            return base64utils.urlsafe_b64decode(text)
        elif is_base64_decodable(text):
            text = force_bytes(text)
            return base64utils.decodebytes(text)
        else:
            return force_bytes(text)
    elif isinstance(text, BYTES_TYPE):
        return text
    else:
        raise TypeError()


def is_chinese_character(c):
    """
    Block                                   Range       Comment
    CJK Unified Ideographs                  4E00-9FFF   Common
    CJK Unified Ideographs Extension A      3400-4DBF   Rare
    CJK Unified Ideographs Extension B      20000-2A6DF Rare, historic
    CJK Unified Ideographs Extension C      2A700–2B73F Rare, historic
    CJK Unified Ideographs Extension D      2B740–2B81F Uncommon, some in current use
    CJK Unified Ideographs Extension E      2B820–2CEAF Rare, historic
    CJK Compatibility Ideographs            F900-FAFF   Duplicates, unifiable variants, corporate characters
    CJK Compatibility Ideographs Supplement 2F800-2FA1F Unifiable variants
    """
    c = ord(c)
    if 0x4E00 <= c <= 0x9FFF:
        return True
    if 0x3400 <= c <= 0x4DBF:
        return True
    if 0x20000 <= c <= 0x2A6DF:
        return True
    if 0x2A700 <= c <= 0x2B73F:
        return True
    if 0x2B740 <= c <= 0x2B81F:
        return True
    if 0x2B820 <= c <= 0x2CEAF:
        return True
    if 0xF900 <= c <= 0xFAFF:
        return True
    if 0x2F800 <= c <= 0x2FA1F:
        return True
    return False


def binarify(data):
    """Turn bytes into binary string. Similar to binascii.hexlify(), but using binary instread hex.

    Examples:

    In [11]: strutils.binarify(b'0')
    Out[11]: '00110000'

    In [12]: strutils.binarify(b'a')
    Out[12]: '01100001'

    In [13]: strutils.binarify(b'hello')
    Out[13]: '0110100001100101011011000110110001101111'
    """
    data = bytes_to_array(data)
    return "".join(["{:08b}".format(ord(x)) for x in data])


def unbinarify(text):
    if not text:
        return b""
    text = force_text(text)
    from zenutils import listutils

    return b"".join([bchar(int(x, 2)) for x in listutils.chunk(text, 8)])


def substrings(value, lengths=None):
    value = value or ""
    subs = set()
    if lengths is None:
        lengths = list(range(len(value)))
    elif isinstance(lengths, int):
        lengths = [lengths]
    for length in lengths:
        for start in range(len(value) - length + 1):
            sub = value[start:start + length]
            subs.add(sub)
    return subs


def combinations2(values, length):
    """同combinations，使用了itertools.product实现，简化了实现逻辑。但性能仅为combinations的一半。仅供参考。"""
    results = set()
    min_length = min([len(x) for x in values])
    repeat = int(math.ceil(length / min_length * 2))
    for vs in itertools.product(values, repeat=repeat):
        line = "".join(vs)
        line_length = len(line)
        max_start_index = line_length - length
        for index in range(max_start_index + 1):
            word = line[index:index + length]
            results.add(word)
    return results


def combinations(values, length):
    """取values中各字符串的任意连接（可重复取），在组成的新字符串中，取任意指定长度子串所形成的集合。

    例如：

    In [96]: strutils.combinations(['abc', 'xyz'], 5)
    Out[96]:
    {'abcab',
    'abcxy',
    'bcabc',
    'bcxyz',
    'cabca',
    'cabcx',
    'cxyza',
    'cxyzx',
    'xyzab',
    'xyzxy',
    'yzabc',
    'yzxyz',
    'zabca',
    'zabcx',
    'zxyza',
    'zxyzx'}

    """
    values = list(values)
    min_length = min([len(x) for x in values])
    max_length = max([len(x) for x in values])
    repeat = int(math.ceil((length * 1.0 - min_length) / min_length))
    repeat_incr = False
    if length <= min_length:
        repeat_incr = True
    if length % min_length == 2 and length % max_length == 2:
        repeat_incr = True
    if length % min_length == 0 and length % max_length == 0:
        repeat_incr = True
    if repeat_incr:
        repeat += 1
    check_length = length + 2 * max_length - 1
    good_words = set()
    short_words = set(values)
    for _ in range(repeat):
        new_words = set()
        for value in values:
            for word in short_words:
                new_word = word + value
                if len(new_word) >= check_length:
                    good_words.add(new_word)
                else:
                    new_words.add(new_word)
        short_words = new_words
        if not short_words:
            break
    for x in short_words:
        if len(x) >= length:
            good_words.add(x)
    result_words = set()
    for word in good_words:
        for subword in substrings(word, length):
            result_words.add(subword)
    return result_words


def captital_number(
    value,
    yuan=default_cn_yuan,
    digits=default_cn_digits,
    places=default_cn_places,
    negative=default_cn_float_places,
    float_places=default_cn_float_places,
):
    from zenutils.numericutils import float_split

    sign, int_part, float_part = float_split(value, precision=7)

    def parse4(parse4_value):
        qian = parse4_value // QIAN
        parse4_value = parse4_value % QIAN
        bai = parse4_value // BAI
        parse4_value = parse4_value % BAI
        shi = parse4_value // SHI
        parse4_value = parse4_value % SHI
        ge = parse4_value
        return (
            digits[qian]
            + places[2]
            + digits[bai]
            + places[1]
            + digits[shi]
            + places[0]
            + digits[ge]
        )

    def parse8(parse8_value):
        high = parse8_value // WAN
        low = parse8_value % WAN
        return parse4(high) + places[3] + parse4(low)

    def parse(pase_value):
        yis = []
        while pase_value:
            yis.append(pase_value % YI)
            pase_value //= YI
        yis.reverse()
        return places[4].join([parse8(x) for x in yis])

    def remove0(value_string):
        z0 = digits[0]
        z00 = digits[0] + digits[0]
        for place in places:
            value_string = value_string.replace(digits[0] + place, digits[0])
        while z00 in value_string:
            value_string = value_string.replace(z00, z0)
        if value_string.startswith(z0):
            value_string = value_string[1:]
        if value_string.endswith(z0):
            value_string = value_string[:-1]
        return value_string

    def parse_float_part(parse_float_part_value):
        if not value:
            return ""
        parse_float_part_result = ""
        for index, c in enumerate("{:07d}".format(parse_float_part_value)):
            if index > len(float_places):
                break
            cv = int(c)
            if cv:
                parse_float_part_result += digits[cv] + float_places[index]
        return parse_float_part_result

    int_string = parse(int_part)
    int_string = remove0(int_string)
    if not int_string:
        int_string = digits[0]

    float_string = parse_float_part(float_part)

    result = int_string + yuan + float_string
    if sign < 0:
        result = negative + result

    return result


def clean(value, keep_chars):
    """Clean the string value and only keep characters in keep_chars.

    @Returns:
        (str or bytes): Cleaned new value which it's chars are all in keep_chars.

    @Parameters:
        value(str or bytes): The string to be cleaned.
        keep_chars(str or bytes): The good characters will be kept.

    @Note:
        The two parameters' type must be the same.
    """
    if not isinstance(keep_chars, set):
        keep_chars = set(bstr_to_array(keep_chars))
    empty = force_type_to("", value)
    vs = [x for x in bstr_to_array(value) if x in keep_chars]
    return empty.join(vs)


do_clean = clean  # Alias of clean


def camel(
    value,
    clean=False,
    keep_chars=string.ascii_letters + string.digits,
    lower_first=False,
):
    if value is None:
        return None
    words = []
    word_chars = set(string.ascii_letters)
    word = ""
    non_word = ""
    for c in value:
        if c in word_chars:
            word += c
            if non_word:
                words.append(non_word)
                non_word = ""
        else:
            non_word += c
            if word:
                words.append(word.capitalize())
                word = ""
    if word:
        words.append(word.capitalize())
    if non_word:
        words.append(non_word)
    if clean:
        keep_chars = set(keep_chars)
        result = "".join([do_clean(x, keep_chars) for x in words])
    else:
        result = "".join(words)
    if len(result) < 1:
        return result
    if lower_first:
        result = result[0].lower() + result[1:]
    return result


def no_mapping(value):
    return value


def none_to_empty_string(value):
    """Turn None to empty string.

    @Returns:
        (Any): If value is None, returns empty string, or else returns value itself.

    @Parameters:
        value(Any): The value to be transformed.
    """
    if value is None:
        return ""
    else:
        return value


def strip_string(value):
    """If value is str, then do string strip, or else returns the value itself.

    @Returns:
        (Any): strip value.

    @Parameters:
        value(Any): The value to be strip. Only str/bytes typed value will be stripped.
    """
    if isinstance(value, (STR_TYPE, BYTES_TYPE)):
        return value.strip()
    else:
        return value


def format_with_mapping(template, mapping, *args, **kwargs):
    def trans(trans_value):
        if callable(mapping):
            return mapping(trans_value)
        else:
            return mapping.get(trans_value, trans_value)

    new_args = []
    new_kwargs = {}
    names = re.findall("{([^}:]*)", template)
    counter = 0
    for index in range(len(names)):
        if names[index] == "":
            names[index] = counter
            counter += 1
        elif names[index].isdigit():
            names[index] = int(names[index])
    ps_args = [x for x in names if isinstance(x, int)]
    if ps_args:
        max_args_index = max(ps_args)
        for index in range(max_args_index + 1):
            if index in names:
                value = trans(args[index])
            else:
                value = None
            new_args.append(value)
    for key, value in kwargs.items():
        if key in names:
            value = trans(kwargs[key])
        new_kwargs[key] = value
    return template.format(*new_args, **new_kwargs)


default_quotes = [
    '"""',  # quote left and quote right are the same
    "'''",
    '"',
    "'",
    "`",
    ("“", "”"),  # quote left and quote right are NOT the same
    ("‘", "’"),
    ("『", "』"),
    ("「", "」"),
    ("﹁", "﹂"),
    ("﹃", "﹄"),
    ("｢", "｣"),
]


def unquote(value, quotes=None):
    """Trim one level quote. If not quoted, do nothing."""
    quotes = quotes or default_quotes
    for quote_pair in quotes:
        if isinstance(quote_pair, STR_TYPE):
            quote_pair = (quote_pair, quote_pair)
        if value.startswith(quote_pair[0]) and value.endswith(quote_pair[1]):
            return value[len(quote_pair[0]):-1 * len(quote_pair[1])]
    return value


def is_uuid(value, allow_bad_characters=False):
    """Test if the value is UUID typed or UUID liked str.

    If allow_bad_characters=True,
    treat c1fd56f3-bd79-42ed-a45c-d711c4032bag liked string as UUID,
    even it contains NON hex character(the last character g is NOT a hex digist).
    """
    if isinstance(value, uuid.UUID):
        return True

    if isinstance(value, (tuple, list)):
        try:
            _ = uuid.UUID(fields=value)
            return True
        except ValueError:
            return False

    if isinstance(value, int):
        try:
            _ = uuid.UUID(int=value)
            return True
        except ValueError:
            return False

    def broken_uuid_check(broken_uuid_check_value):
        broken_uuid_check_value = force_text(broken_uuid_check_value).lower()
        pattern = "^[a-zA-Z0-9]{8}-?[a-zA-Z0-9]{4}-?[a-zA-Z0-9]{4}-?[a-zA-Z0-9]{4}-?[a-zA-Z0-9]{12}$"
        if not re.match(pattern, broken_uuid_check_value):
            return False
        ok_chars = set("0123456789abcdef-")
        bad_chars = 0
        for c in broken_uuid_check_value:
            if c not in ok_chars:
                bad_chars += 1
        if bad_chars > 4:
            return False
        return True

    if isinstance(value, STR_TYPE):
        try:
            _ = uuid.UUID(value)
            return True
        except ValueError:
            if allow_bad_characters:
                return broken_uuid_check(value)
            return False

    if isinstance(value, BYTES_TYPE):
        try:
            _ = uuid.UUID(bytes=value)
            return True
        except ValueError:
            try:
                _ = uuid.UUID(value)
                return True
            except ValueError:
                if allow_bad_characters:
                    return broken_uuid_check(value)
                return False

    return False


def stringlist_append(string_value, new_element, separator=",", allow_duplicate=True):
    elements = split(string_value, [separator], strip=True)
    if allow_duplicate or (new_element not in elements):
        elements.append(new_element)
    return separator.join(elements)


def html_element_css_append(classes, new_class_name):
    return stringlist_append(
        classes, new_class_name, separator=" ", allow_duplicate=False
    )


def remove_prefix(thestring, prefix):
    if thestring.startswith(prefix):
        return thestring[len(prefix):]
    else:
        return thestring


def remove_suffix(thestring, suffix):
    if thestring.endswith(suffix):
        if len(suffix):
            return thestring[: -len(suffix)]
        else:
            return thestring
    else:
        return thestring


def encodable(value, encoding=default_encoding):
    """Test if the string value can be encoded by special encoding.

    Examples:

    In [11]: strutils.encodable('hello') # ascii letters can be encoded by utf-8 encoding.
    Out[11]: True

    In [12]: strutils.encodable('测试') # 中文 测试 can be encoded by utf-8 encoding.
    Out[12]: True

    In [13]: strutils.encodable('测试', encoding='big5') # 中文 测试 can NOT be encoded by big5 encoding.
    Out[13]: False

    """
    try:
        value.encode(encoding)
        return True
    except UnicodeEncodeError:
        return False


def decodable(value, encoding=default_encoding):
    """Test if the bytes value can be decoded by special encoding.

    Examples:

    In [2]: strutils.decodable('测试'.encode('gbk')) # string encoded by gbk can not be decoded by utf-8
    Out[2]: False

    In [3]: strutils.decodable('测试'.encode('gbk'), encoding='gbk') # string encoded by gbk can be decoded by gbk
    Out[3]: True

    """
    try:
        value.decode(encoding)
        return True
    except UnicodeDecodeError:
        return False


def chunk(value, size):
    """Split string value into chunks. Chunk size must be greater than 0.

    Examples:

    In [33]: strutils.chunk('hello', 3)
    Out[33]: ['hel', 'lo']

    In [34]: strutils.chunk('hello', 6)
    Out[34]: ['hello']

    In [35]: strutils.chunk('hello', 5)
    Out[35]: ['hello']

    """
    if size < 1:
        raise ValueError("chunk size must be greater than 0...")
    if value is None:
        return []
    chunks = []
    length = len(value)
    start = 0
    while start < length:
        chunks.append(value[start:start + size])
        start += size
    return chunks


def get_all_substrings(value):
    """Get all substrings of the value.

    Examples:

    In [4]: strutils.get_all_substrings('a')
    Out[4]: {'a'}

    In [5]: strutils.get_all_substrings('ab')
    Out[5]: {'a', 'ab', 'b'}

    In [6]: strutils.get_all_substrings('abc')
    Out[6]: {'a', 'ab', 'abc', 'b', 'bc', 'c'}

    In [7]: strutils.get_all_substrings('abcd')
    Out[7]: {'a', 'ab', 'abc', 'abcd', 'b', 'bc', 'bcd', 'c', 'cd', 'd'}

    In [8]: strutils.get_all_substrings('abcde')
    Out[8]:
    {'a',
    'ab',
    'abc',
    'abcd',
    'abcde',
    'b',
    'bc',
    'bcd',
    'bcde',
    'c',
    'cd',
    'cde',
    'd',
    'de',
    'e'}
    """
    substrings = set()
    for length in range(len(value)):
        length += 1
        for index in range(len(value) - length + 1):
            substring = value[index:index + length]
            substrings.add(substring)
    return substrings


def reverse(value):
    """Reverse a string.

    @Returns:
        (str): Returns the reversed string.

    @Parameters:
        value(str): The original string.

    @Examples:
        assert strutils.reverse("hello") == "olleh"
        assert strutils.reverse(b"hello") == b"olleh"
    """
    if value is None:
        return None
    empty = force_type_to("", value)
    chars = bstr_to_array(value)
    chars.reverse()
    return empty.join(chars)


def get_image_bytes(image, format="png"):
    """Save PIL image into bytes buffer instread of a disk file.

    @Returns:
        (bytes): The image content bytes.

    @Parameters:
        image(Image, or filename of image, or image bytes): The image to be load content bytes.
        format(str, default to 'png'): If the image is an instance of PIL.Image,
        it needs a format the save the image content.
    """
    if (
        isinstance(image, BYTES_TYPE) and len(image) >= 44
    ):  # the 1x1 webp image takes only 44 bytes
        try:
            # try to open the image, it maybe a filename bytes.
            with open(image, "rb") as fobj:
                pass
        except:
            return image
    if isinstance(image, BASESTRING_TYPES):
        # image is an image filename
        with open(image, "rb") as fobj:
            return fobj.read()
    else:
        # image is PIL.Image object
        buffer = BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()


def get_base64image(image, format="png"):
    """Turn image binary content into base64 encoded string, so that it can be used in image <img src="xxx" /> directly.

    @Returns:
        (str): The image src url string.

    @Parameters:
        image(Image, or filename of the image, or the image bytes): The image to be transformed.
        format(str, default to 'png'). Format should match the content the image. Can be png, or jpeg, or gif.
    """
    from zenutils import base64utils

    image = get_image_bytes(image)
    return """data:image/{format};base64,{data}""".format(
        format=format,
        data=force_text(base64utils.encodebytes(image)),
    )


def parse_base64image(image):
    """Parse base64 encoded image string.

    @Returns:
        (format, image_bytes)

    @Parameters:
        image(str): base64 encoded image string that can be used in html image tag's src property.

    """
    from zenutils import base64utils

    image = force_text(image)
    header, data = simplesplit(image, ",", maxsplit=1)
    format = re.findall("data:image/(.*);base64", header)[0]
    data = force_bytes(data)
    return format, base64utils.decodebytes(data)


# ##################################################################
# Removed to anotehr module
# ##################################################################


def bytes2ints(*args, **kwargs):
    """See detail to zenutils.numericutils.bytes2ints."""
    from zenutils import numericutils

    return numericutils.bytes2ints(*args, **kwargs)


def ints2bytes(*args, **kwargs):
    """See detail to zenutils.numericutils.ints2bytes."""
    from zenutils import numericutils

    return numericutils.ints2bytes(*args, **kwargs)


def int2bytes(*args, **kwargs):
    """See tail to zenutils.numericutils.int2bytes."""
    from zenutils import numericutils

    return numericutils.int2bytes(*args, **kwargs)


class StrUtils(object):
    """字符串工具类。"""

    @staticmethod
    def random_string(length, choices=default_random_string_choices):
        """Generates a random string of specified length using specified characters.

        In [3]: strutils.random_string(8)
        Out[3]: 'wJhsaYVq'

        In [4]: strutils.random_string(32)
        Out[4]: 'JtYNblzfEFYdgwcTjNiorwucrlHuIeTQ'

        In [5]: import string

        In [8]: strutils.random_string(32, choices=string.ascii_letters+string.punctuation)
        Out[8]: "]ivN^F]v#jPraNLC:F?<}:!'}aox=lKY"

        In [9]: strutils.random_string(32, choices=string.ascii_letters+string.punctuation)
        Out[9]: 'Flx,TOkDV_g&CsHq#l`RZ:(J#eVxENYJ'
        """
        from zenutils import randomutils

        empty = force_type_to("", choices)
        choices = bstr_to_array(choices)
        return empty.join(randomutils.choices(choices, k=length))


random_string = StrUtils.random_string
