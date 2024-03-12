#!/usr/bin/env python
# -*- coding: utf8 -*-
"""日志工具类。
Make logging setup easy. Default logging settings:

```
logging_config = {
   "version": 1,
   "disable_existing_loggers": False,
   "formatters": {
      "default": {
            "format": "{asctime} {levelname} {pathname} {lineno} {module} {funcName} {process} {thread} {message}",
            "style": "{"
      },
      "message_only": {
            "format": "{message}",
            "style": "{",
      },
      "json": {
            "class": "jsonformatter.JsonFormatter",
            "format": {
               "asctime": "asctime",
               "levelname": "levelname",
               "pathname": "pathname",
               "lineno": "lineno",
               "module": "module",
               "funcName": "funcName",
               "process": "process",
               "thread": "thread",
               "message": "message",
            },
      },
   },
   "handlers": {
      "default_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
      },
      "default_file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": logfile,
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "formatter": "default",
      },
      "json_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
      },
      "json_file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": logfile,
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "formatter": "json",
      },
   },
   "loggers": {
   },
   "root": {
      "handlers": ["default_file", "default_console"],
      "level": loglevel,
      "propagate": True,
   }
}
```

Example:

```
from zenutils import logutils

def setup(settings):
    logging_settings = settings.get("logging", {})
    logutils.setup(**logging_settings)

```
"""

from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)
import os
from logging.config import dictConfig
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler
from . import funcutils
from . import dictutils
from . import fsutils

__all__ = [
    "get_console_handler",
    "get_file_handler",
    "get_simple_config",
    "setup",
]


FILE_HANDLER_BACKUP_COUNT = 90


def get_console_handler(formatter="default", loglevel="DEBUG", handler_class=None):
    """Make a console handler settings."""
    handler_class = handler_class or StreamHandler
    default_params = {
        "level": loglevel,
        "formatter": formatter,
    }
    params = funcutils.get_inject_params(handler_class, default_params)
    params["class"] = ".".join([handler_class.__module__, handler_class.__name__])
    params["formatter"] = formatter
    params["level"] = loglevel
    return params


def get_file_handler(
    filename, formatter="default", loglevel="DEBUG", handler_class=None
):
    """Make a file handler settings."""

    handler_class = handler_class or TimedRotatingFileHandler
    default_params = {
        "level": loglevel,
        "filename": filename,
        "when": "midnight",
        "interval": 1,
        "backupCount": FILE_HANDLER_BACKUP_COUNT,
        "formatter": formatter,
        "encoding": "utf-8",
    }
    params = funcutils.get_inject_params(handler_class, default_params)
    params["class"] = ".".join([handler_class.__module__, handler_class.__name__])
    params["formatter"] = formatter
    params["level"] = loglevel
    return params


def get_simple_config(
    logfile=None,
    loglevel=None,
    logfmt=None,
    loggers=None,
    logging=None,
    console_handler_class=None,
    file_handler_class=None,
    log_to_console=True,
    log_to_file=True,
    **kwargs
):
    """Make simple logging settings.

    logfile default to app.log.
    loglevel choices are: DEBUG/INFO/WARNING/ERROR. default to INFO.
    logfmt choices are: default/message_only/json. default to default.
    Use logger parameter to override the default settings' logger sections.
    Use logging parameter to override the whole settings.

    @Example: Simply setup logger
        from zenutils ipmort logutils
        logutils.setup()

    @Example: Override the default formatter
        from zenutils import logutils
        LOGGING = logutils.get_simple_config(formatters={
            "default": {
                "format": "{asctime} {levelname} {module} {funcName} {process} {thread} {message}",
            },
        })
    """

    loggers = loggers or {}
    config = logging or {}
    # default log file to `pwd`/logs/app.log
    logfile = logfile or config.get("logfile", "./logs/app.log")
    loglevel = loglevel or config.get("loglevel", "INFO")
    logfmt = logfmt or config.get("logfmt", "default")
    # make sure log folder exists...
    logfolder = os.path.abspath(os.path.dirname(logfile))
    fsutils.mkdir(logfolder)
    # default logging template
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(process)s %(thread)s %(module)s %(funcName)s %(lineno)s %(message)s",
            },
            "simple": {
                "format": "%(asctime)s %(levelname)s %(message)s",
            },
            "message_only": {
                "format": "%(message)s",
            },
        },
        "handlers": {},
        "loggers": {},
        "root": {
            "handlers": [],
            "level": loglevel,
            "propagate": True,
        },
    }
    if log_to_console:
        dictutils.deep_merge(
            logging_config,
            {
                "handlers": {
                    "default_console": get_console_handler(
                        "default", "DEBUG", handler_class=console_handler_class
                    ),
                    "simple_console": get_console_handler(
                        "simple", "DEBUG", handler_class=console_handler_class
                    ),
                    "message_only_console": get_console_handler(
                        "message_only", "DEBUG", handler_class=console_handler_class
                    ),
                },
                "root": {
                    "handlers": [logfmt + "_console"],
                },
            },
        )
    if log_to_file:
        dictutils.deep_merge(
            logging_config,
            {
                "handlers": {
                    "default_file": get_file_handler(
                        logfile, "default", "DEBUG", handler_class=file_handler_class
                    ),
                    "simple_file": get_file_handler(
                        logfile, "simple", "DEBUG", handler_class=file_handler_class
                    ),
                    "message_only_file": get_file_handler(
                        logfile,
                        "message_only",
                        "DEBUG",
                        handler_class=file_handler_class,
                    ),
                },
                "root": {"handlers": [logfmt + "_file"]},
            },
        )
    dictutils.deep_merge(logging_config, config)
    dictutils.deep_merge(logging_config, {"loggers": loggers})
    dictutils.deep_merge(logging_config, kwargs)
    return logging_config


def setup(*args, **kwargs):
    """Using get_simple_config to get the logging settings and enable them.

    Parameters are the same with get_simple_config function.
    """
    config = get_simple_config(*args, **kwargs)
    dictConfig(config)
