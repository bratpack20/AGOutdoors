#!/usr/bin/env python
# -*- coding: utf8 -*-
"""性能测试工具。"""
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

import time

__all__ = [
    "timeit",
]


def timeit(func, args=None, kwargs=None, n=1, i=10000, quiet=False):
    """Get func performance benchmarks by calling the func N times with args and kwargs."""
    avg1s = {}
    avg2s = {}
    rate1s = {}
    rate2s = {}

    args = args or []
    kwargs = kwargs or {}
    s1time = time.time()
    s2time = s1time
    next_report_j = i - 1
    for j in range(n):
        func(*args, **kwargs)
        if j == next_report_j:
            etime = time.time()
            avg1 = (etime - s1time) / (j + 1)
            avg2 = (etime - s2time) / i
            rate1 = (j + 1) / (etime - s1time)
            rate2 = i / (etime - s2time)
            if not quiet:
                print((j + 1), etime, avg1, rate1, avg2, rate2)
            s2time = etime
            next_report_j += i
    if j < next_report_j:
        etime = time.time()
        avg1 = (etime - s1time) / (j + 1)
        avg2 = (etime - s2time) / i
        rate1 = (j + 1) / (etime - s1time)
        rate2 = i / (etime - s2time)
        if not quiet:
            print((j + 1), etime, avg1, rate1, avg2, rate2)
        s2time = etime
    return {
        "total": n,
        "stime": s1time,
        "etime": etime,
        "avg1s": avg1s,
        "avg2s": avg2s,
        "rate1s": rate1s,
        "rate2s": rate2s,
    }
