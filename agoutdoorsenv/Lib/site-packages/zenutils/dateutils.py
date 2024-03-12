#!/usr/bin/env python
# -*- coding: utf8 -*-
"""日期工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
import datetime

__all__ = [
    "get_years",
    "get_months",
    "get_days",
]


def get_years(start_day, end_day):
    """获取[start_day, end_day]间的年份列表，包含start_day, end_day所在年份。"""
    for year in range(start_day.year, end_day.year + 1):
        yield datetime.datetime(year=year, month=1, day=1)


def get_months(start_day, end_day):
    """获取[start_day, end_day]间的月份列表，包含start_day, end_day所在月份。"""
    start_day = datetime.datetime(start_day.year, start_day.month, 1)
    while start_day <= end_day:
        if start_day.day == 1:
            yield start_day
        start_day += datetime.timedelta(days=1)


def get_days(start_day, end_day):
    """获取[start_day, end_day]间的所有日期。"""
    while start_day <= end_day:
        yield start_day
        start_day += datetime.timedelta(days=1)
