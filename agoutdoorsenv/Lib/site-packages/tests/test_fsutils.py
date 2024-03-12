#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *

import time
import uuid
import os
import getpass

import unittest
from zenutils import fsutils

class TestFsUtils(unittest.TestCase):

    def test01(self):
        folder_name = str(uuid.uuid4())
        assert fsutils.mkdir(folder_name)
        assert fsutils.mkdir(folder_name)
        assert fsutils.rm(folder_name)
        assert fsutils.rm(folder_name)

    def test02(self):
        filename = str(uuid.uuid4())
        content = str(uuid.uuid4())
        fsutils.write(filename, content)
        assert fsutils.readfile(filename) == content
        assert fsutils.rm(filename)

    def test03(self):
        filename1 = str(uuid.uuid4())
        content1 = str(uuid.uuid4())
        content2 = str(uuid.uuid4())
        fsutils.write(filename1, content1)
        file_replaced, file_failed = fsutils.file_content_replace(filename1, content1, content2)
        assert os.path.abspath(file_replaced[0]) == os.path.abspath(filename1)
        assert fsutils.readfile(filename1) == content2
        assert fsutils.rm(filename1)

    def test04(self):
        filename = str(uuid.uuid4())
        info1 = fsutils.touch(filename)
        time.sleep(1)
        info2 = fsutils.touch(filename)
        fsutils.rm(filename)
        time.sleep(1)

        assert not os.path.exists(filename)
        assert info1
        assert info2
        assert info2.st_mtime > info1.st_mtime

    def test05(self):
        for i in range(5):
            filenames = []
            for j in range(5):
                filenames.append(str(uuid.uuid4()))
            fsutils.touch(filenames[i])
            filename = fsutils.first_exists_file(*filenames)
            assert filename == os.path.abspath(filenames[i])
            for j in range(5):
                fsutils.rm(filenames[j])

    def test06(self):
        filepath = None
        workspace = None
        with fsutils.TemporaryFile() as fileinstance:
            filepath = fileinstance.filepath
            workspace = fileinstance.workspace
            assert os.path.exists(filepath)
            assert os.path.exists(workspace)
        assert os.path.exists(filepath) == False

    def test07(self):
        default = "file not exists..."
        filename = str(uuid.uuid4())
        result = fsutils.readfile(filename, default=default)
        assert result == default

    def test08(self):
        content = os.urandom(1024)
        with fsutils.TemporaryFile(content=content) as tmpfile:
            tmpfile.open("rb")
            assert tmpfile.read() == content

    def test09(self):
        src = fsutils.TemporaryFile(content="hello world")
        dst = fsutils.TemporaryFile()
        fsutils.filecopy(src.filepath, dst.filepath)
        dst.open("r", encoding="utf-8")
        assert dst.read() == "hello world"
    
    def test10(self):
        src = fsutils.TemporaryFile(content="hello world")
        dst = str(uuid.uuid4())
        fsutils.mkdir(dst)
        try:
            fsutils.filecopy(src.filepath, dst)
            dst_content = fsutils.readfile(os.path.join(dst, src.filename))
            assert dst_content == "hello world"
        finally:
            fsutils.rm(dst)

    def test11(self):
        src = fsutils.TemporaryFile(content="hello world")
        dst = str(uuid.uuid4())
        fsutils.mkdir(dst)
        with self.assertRaises(ValueError):
            fsutils.filecopy(src.filepath, dst, dst_is_a_folder=False)
        fsutils.rm(dst)

    def test12(self):
        src = fsutils.TemporaryFile(content="hello world")
        assert fsutils.readfile(src.filepath, binary=True) == b"hello world"

    def test13(self):
        src = fsutils.TemporaryFile(content="hello world")
        fsutils.rename(src.filepath, src.filepath+".tmp")
        assert fsutils.readfile(src.filepath+".tmp") == "hello world"
        fsutils.rm(src.filepath+".tmp")

    def test14(self):
        uid = str(uuid.uuid4())
        os.environ.setdefault("VAR", uid)
        filename = fsutils.expand("~/$VAR/a.txt")
        assert filename
        assert uid in filename
        assert getpass.getuser() in filename

    def test15(self):
        src = fsutils.TemporaryFile(content="hello world", filename_suffix=".txt")
        info = fsutils.info(src.filepath)
        assert info["ext"] == ".txt"
        assert info["size"] == len("hello world")

    def test16(self):
        assert fsutils.get_size_display(0) == "0B"
        assert fsutils.get_size_display(1) == "1B"
        assert fsutils.get_size_display(1023) == "1023B"
        assert fsutils.get_size_display(1024) == "1KB"
        assert fsutils.get_size_display(1025) == "1.00KB"
        assert fsutils.get_size_display(1030) == "1.01KB"
        assert fsutils.get_size_display(1024*1024) == "1MB"
        assert fsutils.get_size_display(1024*1024+1) == "1.00MB"

    def test17(self):
        filename = str(uuid.uuid4()) + ".txt"
        filename1 = fsutils.get_swap_filename(filename)
        filename2 = fsutils.get_swap_filename(filename)
        assert filename1.startswith("." + filename + ".swap.")
        assert filename1 != filename2

    def test18(self):
        filename = str(uuid.uuid4()) + ".txt"
        for i in range(10):
            data = os.urandom(1024)
            fsutils.safe_write(filename, data)
            assert fsutils.readfile(filename, binary=True) == data
            fsutils.rm(filename)

    def test19(self):
        filename = str(uuid.uuid4()) + ".txt"
        filename1 = fsutils.get_swap_filename(filename, prefix=".hello.")
        filename2 = fsutils.get_swap_filename(filename, prefix=".hello.")
        assert filename1.startswith(".hello." + filename + ".swap.")
        assert filename1 != filename2

    def test20(self):
        filename = str(uuid.uuid4()) + ".txt"
        filename1 = fsutils.get_swap_filename(filename, prefix=".hello.", add_random_suffix=False)
        filename2 = fsutils.get_swap_filename(filename, prefix=".hello.", add_random_suffix=False)
        assert filename1.startswith(".hello." + filename + ".swap")
        assert filename1 == filename2

    def test21(self):
        assert fsutils.get_safe_filename("a.txt") == "a.txt"
        assert fsutils.get_safe_filename("a.exe") == "a.exe"
        assert fsutils.get_safe_filename("CON") == "_CON"
        assert fsutils.get_safe_filename("a/b.txt") == "a_b.txt"
        assert fsutils.get_safe_filename("a\\b.txt") == "a_b.txt"
        assert fsutils.get_safe_filename("a<b.txt") == "a_b.txt"
        assert fsutils.get_safe_filename("a>b.txt") == "a_b.txt"
        assert fsutils.get_safe_filename("a:b.txt") == "a_b.txt"
        assert fsutils.get_safe_filename("a\"b.txt") == "a_b.txt"
        assert fsutils.get_safe_filename("a\'b.txt") == "a_b.txt"
        assert fsutils.get_safe_filename("a.") == "a_"

    def test22(self):
        if os.name == "posix":
            filename = str(uuid.uuid4())
            filename += "a<b.txt"
            assert fsutils.get_safe_filename(filename, for_all_platform=False) == filename
            fsutils.write(filename, filename)
            fsutils.rm(filename)
    