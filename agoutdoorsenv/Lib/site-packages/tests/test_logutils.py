#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

import logging
import unittest
from zenutils import logutils

logger = logging.getLogger(__name__)


class TestLogUtils(unittest.TestCase):
    def test01(self):
        logutils.setup()
        logger.debug("hi")
        logger.info("hi")
        logger.warning("hi")
        logger.error("hi")

    def test02(self):
        config = logutils.get_simple_config()
        assert "default" in config["formatters"]
        assert "message_only" in config["formatters"]
        assert "simple" in config["formatters"]

        assert "default_console" in config["handlers"]
        assert "default_file" in config["handlers"]
        assert "message_only_console" in config["handlers"]
        assert "message_only_file" in config["handlers"]
        assert "simple_console" in config["handlers"]
        assert "simple_file" in config["handlers"]
