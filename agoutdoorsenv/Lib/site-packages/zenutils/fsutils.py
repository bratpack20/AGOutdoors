#!/usr/bin/env python
# -*- coding: utf8 -*-
"""文件工具。"""
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
    "mkdir",
    "rm",
    "filecopy",
    "treecopy",
    "copy",
    "pathjoin",
    "readfile",
    "write",
    "get_temp_workspace",
    "rename",
    "move",
    "file_content_replace",
    "touch",
    "expand",
    "first_exists_file",
    "get_application_config_paths",
    "get_application_config_filepath",
    "info",
    "size_unit_names",
    "size_unit_upper_limit",
    "get_size_deviation",
    "get_unit_size",
    "get_size_display",
    "TemporaryFile",
    "get_swap_filename",
    "safe_write",
    "get_safe_filename",
]

import os
import re
import sys
import time
import shutil
import tempfile
import datetime
from uuid import uuid4
from io import open

try:
    FileExistsError
except NameError:
    FileExistsError = OSError  # required by python 2.7


def mkdir(folder):
    """Create a folder if it's not exists.

    @Returns:
        (bool): True means the folder exists or created.
                False means create the folder failed, or there is already a file take the folder's name.

    @Parameters:
        folder(str): The folder's name.

    @Examples:
        assert fsutils.mkdir("a") is True
        assert fsutils.touch("b")
        assert fsutils.mkdir("b") is False
    """
    folder = os.path.abspath(folder)
    if not os.path.exists(folder):
        try:
            try:
                os.makedirs(folder, exist_ok=True)
            except TypeError:  # fix for py2 that doesn't known the exist_ok parameter
                os.makedirs(folder)
        except FileExistsError:
            pass
    return os.path.exists(folder) and os.path.isdir(folder)


def rm(filename):
    """Make sure a file or a directory has been deleted."""
    if os.path.exists(filename):
        if os.path.isfile(filename):
            os.unlink(filename)
        else:
            shutil.rmtree(filename, ignore_errors=True, onerror=None)
        return not os.path.exists(filename)
    else:
        return True


def filecopy(src, dst, dst_is_a_folder=None):
    """Copy a file from src to dst. If dst_is_a_folder=True, then copy the src file to the dst folder and keeps the same name.

    Exmaples:

        filecopy("a.txt", "b.txt") # copy a.txt to file b.txt.
        filecopy("a.txt", "b") # copy a.txt to file b.
        filecopy("a.txt", "b", dst_is_a_folder=True) # copy a.txt to file b/a.txt.

    """
    if dst_is_a_folder is None:
        if os.path.exists(dst) and os.path.isdir(dst):
            dst_is_a_folder = True
        else:
            dst_is_a_folder = False
    elif dst_is_a_folder is False:
        if os.path.exists(dst) and os.path.isdir(dst):
            raise ValueError(
                "There is already a folder named: {dst}, you can NOT copy to it with dst_is_a_folder flag is True...".format(
                    dst=dst,
                )
            )
    if dst_is_a_folder:
        src_name = os.path.basename(src)
        dst = os.path.join(dst, src_name)
    shutil.copy2(src, dst)


def treecopy(src, dst, keep_src_folder_name=True):
    """Copy a folder from src to dst. If keep_src_folder_name=True, copy the src folder to the dst folder and keeps the same name."""
    if keep_src_folder_name:
        src_name = os.path.basename(src)
        dst = os.path.join(dst, src_name)
    shutil.copytree(src, dst)


def copy(src, dst, keep_src_folder_name=True, dst_is_a_folder=False):
    if os.path.exists(src):
        if os.path.isfile(src):
            filecopy(src, dst, dst_is_a_folder)
        else:
            treecopy(src, dst, keep_src_folder_name)


def pathjoin(path1, path2):
    """Concat two paths."""
    return os.path.abspath(os.path.join(path1, path2))


def readfile(filename, binary=False, encoding="utf-8", default=None):
    """Read content from file. Return default value if the file not exists."""
    if not os.path.exists(filename):
        return default
    if binary:
        with open(filename, "rb") as fobj:
            return fobj.read()
    else:
        with open(filename, "r", encoding=encoding) as fobj:
            return fobj.read()


def write(filename, data, encoding="utf-8"):
    """Write content data to file."""
    folder = os.path.dirname(filename)
    mkdir(folder)
    if isinstance(data, bytes):
        with open(filename, "wb") as fobj:
            fobj.write(data)
    else:
        with open(filename, "w", encoding=encoding) as fobj:
            fobj.write(data)


def get_swap_filename(filename, prefix=".", suffix=".swap", add_random_suffix=True):
    """Get a swap filename."""
    from zenutils import strutils

    folder, filename = os.path.split(filename)
    final_filename = ""
    if prefix:
        final_filename += prefix
    final_filename += filename
    if suffix:
        final_filename += suffix
    if add_random_suffix:
        final_filename += "." + strutils.random_string(8)
    return os.path.join(folder, final_filename)


def safe_write(
    filename,
    data,
    encoding="utf-8",
    swap_prefix=".",
    swap_suffix=".swap",
    swap_add_random_suffix=True,
):
    """Write content to a swap file and then rename it to the target filename."""
    swap_filename = get_swap_filename(
        filename,
        prefix=swap_prefix,
        suffix=swap_suffix,
        add_random_suffix=swap_add_random_suffix,
    )
    write(swap_filename, data, encoding)
    rename(swap_filename, filename)


def get_temp_workspace(prefix="", makedir=True):
    """Create a temp folder and return it's path.

    @todo: the new workspace folder should be deleted after use.
    """
    folder_name = prefix + str(uuid4())
    path = os.path.abspath(os.path.join(tempfile.gettempdir(), folder_name))
    if makedir:
        mkdir(path)
    return path


def rename(filepath, name):
    """Only change filename or directory name, but CAN not change the path, e.g. /a/b.txt -> /a/c.txt is ok, /a/b.txt -> /b/b.txt is NOT ok."""
    name = os.path.basename(name)
    folder = os.path.dirname(filepath)
    dst = os.path.abspath(os.path.join(folder, name))
    os.rename(filepath, dst)
    return dst


def move(src, dst):
    """Move a file or a folder to another place."""
    os.rename(src, dst)


def file_content_replace(
    filename,
    original,
    replacement,
    binary=False,
    encoding="utf-8",
    ignore_errors=True,
    **kwargs
):
    """Repleace file content.

    filename: The file to be replace. If filename is a folder name, then all files under the folder will be replaced.
    original: String to be replace. The string will be removed from the file.
    replacement: String used to do replace. The string will be appear in the file.
    """
    file_replaced = []
    file_failed = {}

    def replace(filename, original, replacement, binary=False, encoding="utf-8"):
        content = readfile(filename, binary, encoding)
        content = content.replace(original, replacement)
        write(filename, content, encoding)

    if os.path.isfile(filename):
        try:
            replace(filename, original, replacement, binary, encoding)
            file_replaced.append(filename)
        except Exception as error:
            file_failed[filename] = error
            if not ignore_errors:
                raise error
    else:
        folder = filename
        for root, _, files in os.walk(folder):
            for filename in files:
                path = os.path.abspath(os.path.join(root, filename))
                try:
                    replace(path, original, replacement, binary, encoding)
                    file_replaced.append(path)
                except Exception as error:
                    file_failed[path] = error
                    if not ignore_errors:
                        raise error

    return file_replaced, file_failed


def touch(filename):
    """Make sure a file exists"""
    if os.path.exists(filename):
        os.utime(filename, (time.time(), time.time()))
    else:
        with open(filename, "wb") as _:
            pass
    return os.stat(filename)


def expand(filename):
    """Expand user and expand vars.

    @Returns:
        (str): Returns expended filename.

    @Parameters:
        filename(str): The filename template to be expanded.

    @Examples:
        asserts fsutils.expand("~/a.txt") == "/Users/test/a.txt"
    """
    return os.path.abspath(os.path.expandvars(os.path.expanduser(filename)))


def expands(*filenames):
    """Expand user and expand vars for the given filenames.

    @Returns:
        (list of string): Returns expended filenames.

    @Parameters:
        *filenames(str, multiple): Filenames.

    @Example:
        assert fsutils.expends("~/a.txt") == ["/Users/test/a.txt"]
    """
    results = []
    for filename in filenames:
        results.append(expand(filename))
    return results


def first_exists_file(*filenames, **kwargs):
    """Return the first exists file's abspath. If none file exists, return None.

    @Returns:
        (str): The first exists file's abspath.

    @Parameters:
        *filenames(str, multiple): Filenames.
        default(str or None, keyword parameter): The default filename if all the given filenames is not exists.

    @Examples:
        assert first_exists_file("a.txt", "b.txt", "c.txt", default="failback.txt") == "failback.txt"
    """
    default = kwargs.get("default", None)
    for filename in filenames:
        filename = expand(filename)
        if os.path.exists(filename):
            return os.path.abspath(filename)
    return default


def get_application_config_paths(appname, name="config", suffix="yml"):
    return expands(
        "./{0}-{1}.{2}".format(appname, name, suffix),
        "./conf/{0}-{1}.{2}".format(appname, name, suffix),
        "./etc/{0}-{1}.{2}".format(appname, name, suffix),
        "~/.{0}/{1}.{2}".format(appname, name, suffix),
        "~/{0}/{1}.{2}".format(appname, name, suffix),
        "./{0}.{1}".format(name, suffix),
        "./conf/{0}.{1}".format(name, suffix),
        "./etc/{0}.{1}".format(name, suffix),
        "~/{0}.{1}".format(name, suffix),
        "~/.{0}.{1}".format(name, suffix),
        "{0}.{1}".format(name, suffix),
    )


def get_application_config_filepath(appname, name="config", suffix="yml"):
    """Get application config filepath by search these places:
    ./{appname}-{name}.{suffix}
    ./conf/{appname}-{name}.{suffix}
    ./etc/{appname}-{name}.{suffix}
    ~/.{appname}/{name}.{suffix}
    ~/{appname}/{name}.{suffix}
    ./{name}.{suffix}
    ./conf/{name}.{suffix}
    ./etc/{name}.{suffix}
    ~/{name}.{suffix}
    ~/.{name}.{suffix}
    {name}.{suffix}
    """
    paths = get_application_config_paths(appname, name, suffix)
    return first_exists_file(*paths)


def info(filename):
    """Get file information.

    In [1]: from zenutils import fsutils

    In [2]: fsutils.info('README.md')
    Out[2]:
    {
        'ext': '.md',
        'abspath': 'C:\\\\workspace\\\\zenutils\\\\README.md',
        'size': 10134,
        'atime': datetime.datetime(2022, 1, 21, 11, 17, 11, 490636),
        'ctime': datetime.datetime(2021, 12, 2, 9, 39, 13, 188155),
        'mode': 33206
    }
    """
    ext = os.path.splitext(filename)[1]
    stat = os.stat(filename)
    return {
        "ext": ext,
        "abspath": os.path.abspath(filename),
        "size": stat.st_size,
        "atime": datetime.datetime.fromtimestamp(stat.st_atime),
        "ctime": datetime.datetime.fromtimestamp(stat.st_ctime),
        "mode": stat.st_mode,
    }


size_unit_names = [
    "B",
    "KB",
    "MB",
    "GB",
    "TB",
    "PB",
    "EB",
    "ZB",
    "YB",
]

size_unit_upper_limit = [1024 ** (index + 1) for index, _ in enumerate(size_unit_names)]


def get_size_deviation(unit_name):
    """Get the deviation of 1000-based-size and 1024-based-size.

    In [37]: from zenutils import fsutils

    In [38]: for unit_name in fsutils.size_unit_names:
        ...:     print(unit_name, "=>", fsutils.get_size_deviation(unit_name))
        ...:
    B => 0.0                        # no deviation, always the same.
    KB => 0.0234375                 # 1000-based-size is 2.34375 % less than 1024-based-size.
    MB => 0.04632568359375
    GB => 0.06867742538452148
    TB => 0.09050529822707176
    PB => 0.11182158029987477
    EB => 0.13263826201159645
    ZB => 0.15296705274569966
    YB => 0.17281938744697234       # 1000-based-size is 17.281938744697234 % less than 1024-based-size.

    """
    unit_name = unit_name.upper()
    x = size_unit_names.index(unit_name)
    return 1 - (1000**x) / (1024**x)


def get_unit_size(unit_name, kb_size=1024):
    """base is the size of KB, choices are 1000 or 1024."""
    unit_name = unit_name.upper()
    if not unit_name.endswith("B"):
        unit_name += "B"
    return kb_size ** size_unit_names.index(unit_name)


def get_size_display(size_in_bytes, gap=""):
    """Turn size in bytes to human readable display.

    In [35]: from zenutils import fsutils

    In [36]: for i in range(30):
        ...:     value = 10**i
        ...:     print(value, "=>", fsutils.get_size_display(value))
        ...:
    1 => 1 B
    10 => 10 B
    100 => 100 B
    1000 => 1000 B
    10000 => 9.77 KB
    100000 => 97.66 KB
    1000000 => 976.56 KB
    10000000 => 9.54 MB
    100000000 => 95.37 MB
    1000000000 => 953.67 MB
    10000000000 => 9.31 GB
    100000000000 => 93.13 GB
    1000000000000 => 931.32 GB
    10000000000000 => 9.09 TB
    100000000000000 => 90.95 TB
    1000000000000000 => 909.49 TB
    10000000000000000 => 8.88 PB
    100000000000000000 => 88.82 PB
    1000000000000000000 => 888.18 PB
    10000000000000000000 => 8.67 EB
    100000000000000000000 => 86.74 EB
    1000000000000000000000 => 867.36 EB
    10000000000000000000000 => 8.47 ZB
    100000000000000000000000 => 84.7 ZB
    1000000000000000000000000 => 847.03 ZB
    10000000000000000000000000 => 8.27 YB
    100000000000000000000000000 => 82.72 YB
    1000000000000000000000000000 => 827.18 YB
    10000000000000000000000000000 => 8271.81 YB
    100000000000000000000000000000 => 82718.06 YB
    """
    final_index = 0
    final_upper_limit = 1
    for index, upper_limit in enumerate(size_unit_upper_limit[:-1]):
        if upper_limit > size_in_bytes:
            break
        final_index = index + 1
        final_upper_limit = upper_limit
    display = "{0:.2f}".format(size_in_bytes / final_upper_limit)
    if size_in_bytes % final_upper_limit == 0:
        display = display.rstrip("0").rstrip(".")
    return display + gap + size_unit_names[final_index]


class TemporaryFile(object):
    """Temporary file manager class.

    In [9]: from zenutils import fsutils

    In [10]: filepath = None
        ...: with fsutils.TemporaryFile() as fman:
        ...:     filepath = fman.filepath
        ...:     print(fman.filename)
        ...:     print(fman.filepath)
        ...:     with open(fman.filepath, 'w', encoding='utf-8') as fobj:
        ...:         fobj.write('hello')
        ...:     print(fsutils.readfile(fman.filepath))
        ...: print(fsutils.readfile(filepath))
    639f49cf-e3be-42b6-923b-1c5c37c024fb
    C:\\Users\\test\\AppData\\Local\\Temp\\639f49cf-e3be-42b6-923b-1c5c37c024fb
    hello # in the with block, the temporary file exists and can read content
    None  # out of the with block, the temporary file is deleted and can NOT be read

    In [11]: import os

    In [12]: os.path.exists(filepath) # out of the with block, the temporary file is deleted
    Out[12]: False

    In [13]: filepath
    Out[13]: 'C:\\\\Users\\\\\test\\\\AppData\\\\Local\\\\Temp\\\\639f49cf-e3be-42b6-923b-1c5c37c024fb'
    """

    def __init__(
        self,
        content=None,
        encoding="utf-8",
        workspace=None,
        filename_prefix="",
        filename_suffix="",
        touch_file=True,
    ):
        self.workspace = workspace or tempfile.gettempdir()
        mkdir(self.workspace)
        self.filename = filename_prefix + str(uuid4()) + filename_suffix
        self.filepath = os.path.join(self.workspace, self.filename)
        if content:
            write(self.filepath, content, encoding)
        elif touch_file:
            touch(self.filepath)
        self.fobj = None

    def __enter__(self):
        """Start of the with scope."""
        return self

    def __exit__(self, type, value, traceback):
        """End of the with scope."""
        self.close()
        self.delete()

    def __del__(self):
        """When the TemporaryFile instance is deleting, close the file handler and delete the file first."""
        self.close()
        self.delete()

    def delete(self):
        """Delete the temporary file. Will be automatically called when the TemporaryFile instance deleting."""
        if self.filepath and os.path.exists(self.filepath):
            os.unlink(self.filepath)

    def open(self, *args, **kwargs):
        """Open or Reopen the file and get it's file handler.

        Example:

        In [8]: with fsutils.TemporaryFile(b"hello") as fman:
        ...:     fobj = fman.open("rb")
        ...:     msg = fobj.read()
        ...:     print(msg)
        ...:     fobj = fman.open("wb")
        ...:     fobj.write(b"hi")
        ...:     fobj = fman.open("rb")
        ...:     msg = fobj.read()
        ...:     print(msg)
        b'hello'
        b'hi'

        """
        self.close()
        self.fobj = open(self.filepath, *args, **kwargs)
        return self

    def close(self):
        """Close the file handler. Will be automatically called when the TemporaryFile instance deleting."""
        if self.fobj:
            self.fobj.close()
            self.fobj = None

    @property
    def buffer(self):
        return self.fobj.buffer

    @property
    def closed(self):
        return self.fobj.closed

    def detach(self, *args, **kwargs):
        return self.fobj.detach(*args, **kwargs)

    @property
    def encoding(self):
        return self.fobj.encoding

    @property
    def errors(self):
        return self.fobj.errors

    def fileno(self, *args, **kwargs):
        return self.fobj.fileno(*args, **kwargs)

    def flush(self, *args, **kwargs):
        return self.fobj.flush(*args, **kwargs)

    def isatty(self, *args, **kwargs):
        return self.fobj.isatty(*args, **kwargs)

    @property
    def line_buffering(self):
        return self.fobj.line_buffering

    @property
    def mode(self):
        return self.fobj.mode

    @property
    def name(self):
        return self.fobj.name

    @property
    def newlines(self):
        return self.fobj.newlines

    def read(self, *args, **kwargs):
        return self.fobj.read(*args, **kwargs)

    def readable(self, *args, **kwargs):
        return self.fobj.readable(*args, **kwargs)

    def readline(self, *args, **kwargs):
        return self.fobj.readline(*args, **kwargs)

    def readlines(self, *args, **kwargs):
        return self.readlines(*args, **kwargs)

    def reconfigure(self, *args, **kwargs):
        return self.fobj.reconfigure(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self.fobj.seek(*args, **kwargs)

    def seekable(self, *args, **kwargs):
        return self.fobj.seekable(*args, **kwargs)

    def truncate(self, *args, **kwargs):
        return self.fobj.truncate(*args, **kwargs)

    def writable(self, *args, **kwargs):
        return self.fobj.writable(*args, **kwargs)

    def write(self, *args, **kwargs):
        return self.fobj.write(*args, **kwargs)

    @property
    def write_through(self):
        return self.fobj.write_through

    def writelines(self, *args, **kwargs):
        return self.fobj.writelines(*args, **kwargs)


NT_FILENAME_CHAR_REPLACEMENTS = {
    "<": "_",
    ">": "_",
    ":": "_",
    '"': "'",
    "/": "_",
    "\\": "_",
    "|": "_",
    "*": "_",
    "?": "_",
    "\x00": "",
    "\x01": "",
    "\x02": "",
    "\x03": "",
    "\x04": "",
    "\x05": "",
    "\x06": "",
    "\x07": "",
    "\x08": "",
    "\x09": "",
    "\x0A": "",
    "\x0B": "",
    "\x0C": "",
    "\x0D": "",
    "\x0E": "",
    "\x0F": "",
    "\x10": "",
    "\x11": "",
    "\x12": "",
    "\x13": "",
    "\x14": "",
    "\x15": "",
    "\x16": "",
    "\x17": "",
    "\x18": "",
    "\x19": "",
    "\x1A": "",
    "\x1B": "",
    "\x1C": "",
    "\x1D": "",
    "\x1E": "",
    "\x1F": "",
}
POSIX_FILENAME_CHAR_REPLACEMENTS = {
    "/": "_",
    "'": '"',
    "\x00": "",
}
DARWIN_FILENAME_CHAR_REPLACEMENTS = {
    ":": "_",
}
ALL_PLATFORM_FILENAME_CHAR_REPLACEMENTS = {
    "<": "_",
    ">": "_",
    ":": "_",
    '"': "_",
    "'": "_",
    "/": "_",
    "\\": "_",
    "|": "_",
    "*": "_",
    "?": "_",
    "\x00": "",
    "\x01": "",
    "\x02": "",
    "\x03": "",
    "\x04": "",
    "\x05": "",
    "\x06": "",
    "\x07": "",
    "\x08": "",
    "\x09": "",
    "\x0A": "",
    "\x0B": "",
    "\x0C": "",
    "\x0D": "",
    "\x0E": "",
    "\x0F": "",
    "\x10": "",
    "\x11": "",
    "\x12": "",
    "\x13": "",
    "\x14": "",
    "\x15": "",
    "\x16": "",
    "\x17": "",
    "\x18": "",
    "\x19": "",
    "\x1A": "",
    "\x1B": "",
    "\x1C": "",
    "\x1D": "",
    "\x1E": "",
    "\x1F": "",
}
NT_FILENAME_RESERVED = [
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
]
NT_FILENAME_RESERVED = ["^" + x + "(\\..*)?$" for x in NT_FILENAME_RESERVED]

for _key in NT_FILENAME_CHAR_REPLACEMENTS:
    assert _key in ALL_PLATFORM_FILENAME_CHAR_REPLACEMENTS
for _key in POSIX_FILENAME_CHAR_REPLACEMENTS:
    assert _key in ALL_PLATFORM_FILENAME_CHAR_REPLACEMENTS
for _key in DARWIN_FILENAME_CHAR_REPLACEMENTS:
    assert _key in ALL_PLATFORM_FILENAME_CHAR_REPLACEMENTS


def get_safe_filename(filename, for_all_platform=True):
    """Replace bad chars in filename and return the filename safe for create a file.

    The filename MUST be a basename of a filename, MUST NOT include any dir name.

    @Examples:
        assert get_safe_filename("a<b.txt") == "a_b.txt"
        assert get_safe_filename("a/b.txt") == "a_b.txt"
    """
    if for_all_platform:
        for k, v in ALL_PLATFORM_FILENAME_CHAR_REPLACEMENTS.items():
            filename = filename.replace(k, v)
    else:
        if os.name == "nt":
            for k, v in NT_FILENAME_CHAR_REPLACEMENTS.items():
                filename = filename.replace(k, v)
        else:
            for k, v in POSIX_FILENAME_CHAR_REPLACEMENTS.items():
                filename = filename.replace(k, v)
            if sys.platform == "darwin":
                for k, v in DARWIN_FILENAME_CHAR_REPLACEMENTS.items():
                    filename = filename.replace(k, v)
    if for_all_platform or os.name == "nt":
        if filename.endswith("."):
            filename = filename[:-1] + "_"
        for pattern in NT_FILENAME_RESERVED:
            if re.match(pattern, filename):
                filename = "_" + filename
    return filename
