#!/usr/bin/env python
# -*- coding: utf8 -*-
"""HTTP请求工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

__all__ = [
    "urlparse",
    "get_urlinfo",
    "get_url_filename",
    "get_url_save_path",
    "get_sitename",
    "download",
]

import os

try:
    from urllib.parse import urlparse
    from urllib.parse import ParseResult
except ImportError:
    from urlparse import urlparse  # fix for python2.7
    from urlparse import ParseResult

from .sixutils import PY2

DEFAULT_DOWNLOAD_CHUNK_SIZE = 4096


def get_urlinfo(url):
    """Parse url.

    @Returns:
        (ParseResult): The url informations.

    @Parameters:
        url(str): The string of the url.
    """
    if isinstance(url, ParseResult):
        info = url
    else:
        info = urlparse(url)
    return info


def get_url_filename(url, info=None):
    """Get the filename that maybe used to save the content of the url.

    @Returns:
        (str): The final filename.

    @Parameters:
        url(str): The url to be saved.
        info(ParseResult, optional): Info will be used if it is provided.
                                     If not provided, get the info from the url by call get_urlinfo().
    """
    info = info or get_urlinfo(url)
    path = info.path
    filename = os.path.split(path)[1]
    if not filename:
        filename = "index.html"
    return filename


def get_url_save_path(url, save_root, info=None):
    info = info or get_urlinfo(url)
    filename = get_url_filename(url, info)
    path = info.path.split(info.path)[0]
    filepath = os.path.abspath(os.path.join(save_root, "." + path + "/", filename))
    return filepath


def get_sitename(url):
    """Get the hostname of the url.

    @Returns:
        (str): The hostname of the url.

    @Paramters:
        url(str): The url string.
    """
    info = get_urlinfo(url)
    return info.hostname


def download_py2(url, filename):
    """Download implement for py2."""
    import urllib2

    response = urllib2.urlopen(url)
    size = 0
    with open(filename, "wb") as fobj:
        while True:
            chunk = response.read(DEFAULT_DOWNLOAD_CHUNK_SIZE)
            if len(chunk) > 0:
                size += len(chunk)
                fobj.write(chunk)
            else:
                break
    return size


def download_py3(url, filename):
    """Download implement for py3."""
    import http.client

    info = get_urlinfo(url)
    if info.scheme == "https":
        conn = http.client.HTTPSConnection(info.hostname, info.port or 443)
    else:
        conn = http.client.HTTPConnection(info.hostname, info.port or 80)
    path = info.path
    if info.query:
        path += "?" + info.query
    conn.request("GET", path)
    response = conn.getresponse()
    size = 0
    with open(filename, "wb") as fobj:
        while True:
            chunk = response.read(DEFAULT_DOWNLOAD_CHUNK_SIZE)
            if len(chunk) > 0:
                size += len(chunk)
                fobj.write(chunk)
            else:
                break
    return size


def download(url, filename):
    """Simple http get request. Use to download a file from url and save it to a file.

    @Returns:
        (int): Content read size.

    @Paramters:
        url(str): The url to be downloaded.
        filename(str): The filename to be used in saving downloaded file.
    """
    if PY2:
        return download_py2(url, filename)
    else:
        return download_py3(url, filename)
