#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils.sixutils import *

import datetime
import unittest

from zenutils import dateutils

class TestDateUtils(unittest.TestCase):
   
   def test01(self):
        days = list(dateutils.get_days(datetime.datetime(2022, 1, 1), datetime.datetime(2022, 2, 1)))
        assert len(days) == 32

   def test02(self):
        days = list(dateutils.get_days(datetime.datetime(2022, 2, 1), datetime.datetime(2022, 3, 1)))
        assert len(days) == 29

   def test03(self):
        days = list(dateutils.get_months(datetime.datetime(2022, 2, 1), datetime.datetime(2022, 3, 1)))
        assert len(days) == 2

   def test04(self):
        days = list(dateutils.get_years(datetime.datetime(2022, 2, 1), datetime.datetime(2022, 3, 1)))
        assert len(days) == 1

   def test04(self):
        days = list(dateutils.get_years(datetime.datetime(2021, 2, 1), datetime.datetime(2022, 3, 1)))
        assert len(days) == 2

   def test05(self):
        days = list(dateutils.get_months(datetime.datetime(2021, 2, 1), datetime.datetime(2022, 3, 1)))
        assert len(days) == 14

