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

__all__ = [
    "PoolBase",
    "Pool",
]

import sys
import time
import logging
from threading import Lock

try:
    from queue import Queue
    from queue import Empty
except ImportError:
    from Queue import Queue
    from Queue import Empty

import wrapt

SESSION_USAGE_COUNT_PROPERY = "_pooling_usage_count"
SESSION_MARK_FOR_DESTORY_PROPERTY = "_pooling_mark_for_destory"

_logger = logging.getLogger(__name__)


class Counter(object):
    def __init__(self, init_value=0):
        self.value = init_value
        self.lock = Lock()

    def incr(self):
        with self.lock as locked:
            if locked:
                self.value += 1
                return self.value

    def decr(self):
        with self.lock as locked:
            if locked:
                self.value -= 1
                return self.value


class Session(wrapt.ObjectProxy):
    def __init__(self, real_session, pool):
        wrapt.ObjectProxy.__init__(self, real_session)
        self._pooling_real_session = real_session
        self._pooling_pool = pool
        self._pooling_pool_version = pool.version.value
        self._pooling_mark_for_destory_flag = False
        self._pooling_incr_usage_count()  # 使用的次数，而非引用的次数，所以是累加的。

    def __del__(self):
        self.__pooling_del__()

    def __pooling_del__(self):
        if self._pooling_real_session:
            if (
                self._pooling_pool_version != self._pooling_pool.version.value
                or self._pooling_mark_for_destory_flag
                or self._pooling_is_connection_closed()
            ):
                self._pooling_pool.destory_session(self._pooling_real_session)
            else:
                self._pooling_pool.return_session(self._pooling_real_session)
            self._pooling_real_session = None

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.__pooling_del__()

    def _pooling_incr_usage_count(self):
        if hasattr(
            self._pooling_real_session, "__dict__"
        ):  # 如果self._pooling_real_session对象经过代理包装过的话，getattr会失效。只能直接操作__dict__属性。
            if not SESSION_USAGE_COUNT_PROPERY in self._pooling_real_session.__dict__:
                self._pooling_real_session.__dict__[SESSION_USAGE_COUNT_PROPERY] = 0
            self._pooling_real_session.__dict__[SESSION_USAGE_COUNT_PROPERY] += 1
        else:
            setattr(
                self._pooling_real_session,
                SESSION_USAGE_COUNT_PROPERY,
                getattr(self._pooling_real_session, SESSION_USAGE_COUNT_PROPERY, 0) + 1,
            )

    def _pooling_get_usage_count(self):
        if hasattr(
            self._pooling_real_session, "__dict__"
        ):  # 如果self._pooling_real_session对象经过代理包装过的话，getattr会失效。只能直接操作__dict__属性。
            return self._pooling_real_session.__dict__.get(
                SESSION_USAGE_COUNT_PROPERY, 0
            )
        else:
            return getattr(self._pooling_real_session, SESSION_USAGE_COUNT_PROPERY, 0)

    def _pooling_mark_for_destory(self):
        self._pooling_mark_for_destory_flag = True

    def _pooling_destory_session(self):
        self._pooling_mark_for_destory_flag = True
        self._pooling_pool.destory_session(self._pooling_real_session)
        self._pooling_real_session = None

    def _pooling_return_session(self):
        self._pooling_pool.return_session(self._pooling_real_session)
        self._pooling_real_session = None

    def _pooling_is_connection_closed(self):
        return getattr(self._pooling_real_session, "_connection_closed", False)


class PoolBase(object):
    def __init__(self, pool_size, args=None, kwargs=None, ping_test=True, **extra):
        """
        pool_size: The max number of the real session will be created.
        args: args used to make a new real session.
        kwargs: kwargs used to make a new real session.
        """
        self.pool_size = pool_size
        self.create_args = tuple(args or [])
        self.create_kwargs = kwargs or {}
        self.real_sessions = Queue()
        self.counter = Counter()
        self.make_session_lock = Lock()
        self.version = Counter(1)
        self.ping_test = ping_test
        self.extra = extra

    def do_session_create(self, *create_args, **create_kwargs):
        # 重载时，创建失败，返回None或抛出异常
        raise NotImplementedError()

    def do_session_destory(self, real_session):
        # 重载时自行修理异常，不要抛出异常
        pass

    def create_session(self):
        real_session = self.do_session_create(*self.create_args, **self.create_kwargs)
        self.counter.incr()
        return real_session

    def return_session(self, real_session):
        self.real_sessions.put(real_session)

    def destory_session(self, real_session):
        self.do_session_destory(real_session)
        self.counter.decr()

    def get_session(self, timeout=None):
        last_error = Empty("get_session timeout...")
        real_session = None
        stime = time.time()
        c = 0
        while True:
            c += 1
            if timeout and time.time() - stime > timeout:
                raise last_error
            # 从session池中获取一个session
            real_session = self._get_old_session(stime, timeout, c)
            # session池为空，尝试创建一个session
            if real_session is None:
                try:
                    real_session = self._try_to_create_new_session(stime, timeout, c)
                except Exception as error:
                    last_error = error
                    _logger.warning(
                        "PoolBase.get_session create a new session failed: {}".format(
                            error
                        )
                    )
                    real_session = None
            # 如果取到了或创建了session，尝试对这个session做ping测试，以便确定这个session有效
            if real_session and self.ping_test:
                try:
                    real_session.ping()
                except Exception as error:
                    _logger.warning(
                        "PoolBase.get_session do ping test on session {} failed {}: {}".format(
                            real_session, c, error
                        )
                    )
                    last_error = error
                    self.destory_session(real_session)
                    real_session = None

            # 如果获取session失败，休息一段时间后，重新尝试
            if real_session is None:
                if c > 1:
                    _logger.debug(
                        "PoolBase.get_session sleep {} seconds...".format(c * 0.1)
                    )
                    time.sleep((c % 100 + 1) * 0.1)
                continue
            else:
                break
        return Session(real_session, self)

    def _get_old_session(self, stime, timeout, c):
        try:
            if self.counter.value < self.pool_size:
                return self.real_sessions.get_nowait()
            else:
                return self.real_sessions.get(timeout=0.1 * c)
        except Empty:
            return None

    def _try_to_create_new_session(self, stime, timeout, c):
        if self.counter.value < self.pool_size:
            if sys.version_info.major == 2:
                flag = self.make_session_lock.acquire(False)
            else:
                flag = self.make_session_lock.acquire(timeout=0.1 * c)
            if flag:
                try:
                    if self.counter.value < self.pool_size:
                        return self.create_session()
                    else:
                        return None
                finally:
                    self.make_session_lock.release()

    def destory_all_sessions(self):
        # destory all sessions in the queue
        # incr pool version so that old sessions will be deleted while returning to the queue
        self.version.incr()
        while True:
            try:
                session = self.real_sessions.get_nowait()
            except Empty:
                break
            self.destory_session(session)


class Pool(PoolBase):
    def __init__(self, pool_size, create_factory, destory_factory=None):
        PoolBase.__init__(self, pool_size)
        self.create_factory = create_factory
        self.destory_factory = destory_factory

    def do_session_create(self, *create_args, **create_kwargs):
        return self.create_factory()

    def do_session_destory(self, real_session):
        if self.destory_factory:
            self.destory_factory(real_session)
