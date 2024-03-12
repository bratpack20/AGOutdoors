#!/usr/bin/env python
# -*- coding: utf8 -*-
"""线程工具。"""
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

import sys
import time
import logging
import threading

try:
    from queue import Queue
    from queue import Empty
    from queue import Full
except ImportError:
    from Queue import Queue
    from Queue import Empty
    from Queue import Full

from zenutils.sixutils import Interrupted


__all__ = [
    "ConcurrentLimitJobQueue",
    "Counter",
    "StartOnTerminatedService",
    "ServiceStop",
    "ServiceTerminate",
    "LoopIdle",
    "Service",
    "SimpleProducer",
    "SimpleConsumer",
    "SimpleServer",
    "SimpleProducerConsumerServer",
    "JobExecuteTimeout",
    "JobResultNotSet",
    "Future",
    "JobQueue",
]

_logger = logging.getLogger(__name__)


class ConcurrentLimitJobQueue(object):
    """并发任务数可控的任务队列。"""

    def __init__(self, size):
        self.counter = threading.Semaphore(size)
        self.queue = Queue()

    def acquire(self, timeout=30):
        """获取一个任务配额。"""
        if sys.version_info.major == 2:
            for _ in range(int(timeout)):
                if self.counter.acquire(blocking=False):
                    return True
                time.sleep(1)
            return False
        else:
            return self.counter.acquire(timeout=timeout)

    def release(self):
        """翻译一个任务配额。"""
        self.counter.release()

    def put(self, job):
        """提交一个任务。"""
        self.queue.put(job)

    def get(self, timeout=30):
        """提取一个任务"""
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            return None


class Counter(object):
    """Thread safe counter.

    变更数值前先锁定计数器。
    """

    def __init__(self, init_value=0):
        self.lock = threading.Lock()
        self.value = init_value

    def incr(self, delta=1):
        """计数器增加数值。"""
        with self.lock:
            self.value += delta
            return self.value

    def decr(self, delta=1):
        """计数器减少数据。"""
        with self.lock:
            self.value -= delta
            return self.value


class WorkerCounter(object):
    """工作实例计数。支持等待所有工作实例结束。"""

    def __init__(self):
        self.lock = threading.Lock()
        self.event = threading.Event()
        self._value = 0
        self.event.set()

    def incr(self):
        """工作实例启动。"""
        with self.lock:
            self._value += 1
            if self._value != 0 and self.event.is_set():
                self.event.clear()
            return self._value

    def decr(self):
        """工作实例结束。"""
        with self.lock:
            self._value -= 1
            if self._value == 0 and (not self.event.is_set()):
                self.event.set()
            return self._value

    def wait(self, timeout=None):
        """等待所有工作实例结束。"""
        return self.event.wait(timeout=timeout)

    @property
    def value(self):
        """计数值。只读。"""
        return self._value


class StartOnTerminatedService(RuntimeError):
    """不允许重启已经终止的服务。"""


class ServiceStop(RuntimeError):
    """服务关停。允许重启。"""


class ServiceTerminate(RuntimeError):
    """服务终止。不允许重启。"""


class LoopIdle(RuntimeError):
    """工作线程空闲。"""


class Service(object):
    """能用服务包装。"""

    default_service_loop_interval = 1
    default_sleep_interval_in_joining = 1
    default_sleep_interval_after_stopped = 1

    def __init__(
        self,
        service_loop=None,
        service_loop_args=None,
        service_loop_kwargs=None,
        service_loop_interval=None,
        sleep_interval_in_joining=None,
        sleep_interval_after_stopped=None,
        server=None,
        service_name=None,
        on_loop_error=None,
        on_loop_idle=None,
        on_loop_finished=None,
        **kwargs
    ):
        self.service_start_lock = threading.Lock()
        self.service_thread = None

        self.start_time = None
        self.started = None
        self.started_time = None
        self.terminate_flag = False
        self.terminate_time = None
        self.terminated = False
        self.terminated_time = None
        self.stop_flag = None
        self.stop_time = None
        self.stopped = None
        self.stopped_time = None

        self.is_running = False

        self.service_loop_callback = service_loop
        self.service_loop_args = service_loop_args or []
        self.service_loop_kwargs = service_loop_kwargs or {}
        if service_loop_interval is None:
            self.service_loop_interval = self.default_service_loop_interval
        else:
            self.service_loop_interval = service_loop_interval
        self.sleep_interval_in_joining = (
            sleep_interval_in_joining or self.default_sleep_interval_in_joining
        )
        self.sleep_interval_after_stopped = (
            sleep_interval_after_stopped or self.default_sleep_interval_after_stopped
        )
        self.server = server
        self.service_name = service_name or self.service_loop_callback.__name__
        self.on_loop_error_callback = on_loop_error
        self.on_loop_idle_callback = on_loop_idle
        self.on_loop_finished_callback = on_loop_finished

    def start(self):
        """Create the service thread and start the service loop."""
        if self.terminated:
            raise StartOnTerminatedService()
        self.start_time = time.time()
        self.stop_flag = False
        self.stop_time = None
        self.stopped = False
        self.stopped_time = None
        with self.service_start_lock:
            if not self.started:
                self.service_thread = threading.Thread(target=self.main)
                self.service_thread.daemon = True
                self.service_thread.start()
                self.started_time = time.time()
                self.started = True

    def stop(self, wait=True, wait_timeout=-1):
        """Stop the service loop, but keep the service thread, so that it can be resumed."""
        self.stop_time = time.time()
        self.stop_flag = True
        return self.join(wait, wait_timeout)

    def terminate(self, wait=True, wait_timeout=-1):
        """Stop the service loop and exit the service thread. It can not be resumed."""
        self.terminate_time = time.time()
        self.terminate_flag = True
        return self.stop(wait, wait_timeout)

    def join(self, wait=True, wait_timeout=-1):
        """Return True means service stopped, False means not stopped and timeout, None means no waiting..."""
        if not wait:
            if not self.is_running:
                return True
            else:
                return None  # no waiting, so we don't know it's stopped or not
        stime = time.time()
        while self.is_running:
            if wait_timeout >= 0 and time.time() - stime >= wait_timeout:
                return False
            time.sleep(self.sleep_interval_in_joining)
        return True

    def main(self):
        """
        The main control process of the service,
        calling the service_loop process,
        dealing with the stop and terminate events and handling the exceptions.
        """
        while not self.terminate_flag:
            if self.stop_flag:
                self.is_running = False
                if self.stopped_time is None:
                    self.stopped_time = time.time()
                self.stopped = True
                time.sleep(self.sleep_interval_after_stopped)
                continue
            self.is_running = True
            try:
                try:
                    self.service_loop()
                except LoopIdle:
                    self.on_loop_idle()
                except ServiceStop:
                    self.stop(wait=False)
                except Interrupted:
                    self.terminate(wait=False)
                except ServiceTerminate:
                    self.terminate(wait=False)
                except Exception as error:  # pylint: disable=broad-exception-caught
                    self.on_loop_error(error)
                finally:
                    self.on_loop_finished()
            except ServiceStop:
                self.stop(wait=False)
            except Interrupted:
                self.terminate(wait=False)
            except ServiceTerminate:
                self.terminate(wait=False)
            except Exception as error:  # pylint: disable=broad-exception-caught
                _logger.exception(
                    "service main process got unknown error: %s...", error
                )
            if (not self.terminated) and self.service_loop_interval:
                time.sleep(self.service_loop_interval)
        self.terminated_time = time.time()
        self.terminated = True
        self.is_running = False

    def service_loop(self):
        """服务主循环。"""
        _logger.debug("calling service_loop...")
        if self.service_loop_callback and callable(self.service_loop_callback):
            _logger.debug("calling service_loop_callback...")
            self.service_loop_callback(
                *self.service_loop_args, **self.service_loop_kwargs
            )
            _logger.debug("call service_loop_callback finished.")
        _logger.debug("call service_loop finished.")

    def on_loop_idle(self):
        """服务线程空闲时回调。"""
        _logger.debug("calling on_loop_idle...")
        if self.on_loop_idle_callback and callable(self.on_loop_idle_callback):
            try:
                _logger.debug("calling on_loop_idle_callback...")
                self.on_loop_idle_callback()
                _logger.debug("call on_loop_idle_callback finished.")
            except Exception as error:  # pylint: disable=broad-exception-caught
                _logger.exception("calling on_loop_idle_callback failed: %s...", error)
        _logger.debug("call on_loop_idle finished.")

    def on_loop_error(self, error):
        """服务循环过程异常时回调。"""
        _logger.debug("calling on_loop_error: %s...", error)
        if self.on_loop_error_callback and callable(self.on_loop_error_callback):
            try:
                _logger.debug("calling on_loop_error_callback...")
                self.on_loop_error_callback(error)
                _logger.debug("call on_loop_error_callback finished.")
            except Exception as error2:  # pylint: disable=broad-exception-caught
                _logger.exception("call on_loop_error_callback failed: %s...", error2)
        _logger.debug("call on_loop_error finished.")

    def on_loop_finished(self):
        """服务循环过程结束时回调。"""
        _logger.debug("calling on_loop_finished...")
        if self.on_loop_finished_callback and callable(self.on_loop_finished_callback):
            try:
                _logger.debug("calling on_loop_finished_callback...")
                self.on_loop_finished_callback()
                _logger.debug("call on_loop_finished_callback finished.")
            except Exception as error:  # pylint: disable=broad-exception-caught
                _logger.exception("call on_loop_finished_callback failed: %s...", error)
        _logger.debug("call on_loop_finished finished.")


class SimpleProducer(Service):
    """简易的生产者。"""

    is_producer = True
    is_consumer = False
    default_task_queue_put_timeout = 1

    def __init__(
        self,
        task_queue,
        produce=None,
        produce_args=None,
        produce_kwargs=None,
        task_queue_put_timeout=None,
        **kwargs
    ):
        self.task_queue = task_queue
        self.produce_callback = produce
        self.produce_callback_args = produce_args or []
        self.produce_callback_kwargs = produce_kwargs or {}
        if task_queue_put_timeout is None:
            self.task_queue_put_timeout = self.default_task_queue_put_timeout
        else:
            self.task_queue_put_timeout = task_queue_put_timeout
        self.produced_counter = Counter()
        super(SimpleProducer, self).__init__(**kwargs)

    def service_loop(self):
        """SimpleProducer service_loop is making tasks and putting the tasks into task queue."""
        _logger.debug("SimpleProducer doing service_loop, and making tasks...")
        tasks = self.produce()
        _logger.debug("SimpleProducer made tasks: %s...", tasks)
        if tasks:
            delta = len(tasks)
            _logger.debug(
                "SimpleProducer icnring produced_counter, value += %s.", delta
            )
            self.produced_counter.incr(delta)
        _logger.debug("SimpleProducer putting tasks into task queue...")
        for task in tasks:
            while True:
                try:
                    _logger.debug(
                        "SimpleProducer putting task into task_queue: %s...", task
                    )
                    self.task_queue.put(task, timeout=self.task_queue_put_timeout)
                    _logger.debug("SimpleProducer put task done, task: %s...", task)
                    break
                except Full:
                    _logger.debug(
                        "SimpleProducer put task into task_queue failed because the task_queue is full, try again, task: %s...",
                        task,
                    )

    def produce(self):
        """生产。"""
        _logger.debug(
            "SimpleProducer is making tasks and calling the produce_callback..."
        )
        if self.produce_callback and callable(self.produce_callback):
            _logger.debug(
                "SimpleProducer is calling produce_callback: args=%s kwargs=%s...",
                self.produce_callback_args,
                self.produce_callback_kwargs,
            )
            tasks = self.produce_callback(
                *self.produce_callback_args, **self.produce_callback_kwargs
            )
            _logger.debug("SimpleProducer call SimpleProducer finished.")
        else:
            _logger.debug(
                "SimpleProducer has NO produce_callback, return empty tasks..."
            )
            tasks = []
        _logger.debug("SimpleProducer call produce_callback done, tasks: %s...", tasks)
        return tasks


class SimpleConsumer(Service):
    """简易消费者。"""

    is_producer = False
    is_consumer = True
    default_task_queue_get_timeout = 1

    def __init__(
        self,
        task_queue,
        consume=None,
        consume_args=None,
        consume_kwargs=None,
        task_queue_get_timeout=None,
        **kwargs
    ):
        self.task_queue = task_queue
        self.consume_callback = consume
        self.consume_callback_args = consume_args or []
        self.consume_callback_kwargs = consume_kwargs or {}
        if task_queue_get_timeout is None:
            self.task_queue_get_timeout = self.default_task_queue_get_timeout
        else:
            self.task_queue_get_timeout = task_queue_get_timeout
        self.consumed_counter = Counter()
        super(SimpleConsumer, self).__init__(**kwargs)

    def service_loop(self):
        """SimpleConsume service_loop is getting tasks from the task_queue, and handling the tasks."""
        _logger.debug(
            "SimpleConsume doing service_loop, and getting task from task_queue..."
        )
        try:
            task = self.task_queue.get(timeout=self.task_queue_get_timeout)
            _logger.debug("SimpleConsume got a task: %s...", task)
        except Empty:
            _logger.debug("SimpleConsume got NO task...")
            raise LoopIdle()  # pylint: disable=raise-missing-from
        _logger.debug("SimpleConsume icnring consumed_counter, value += 1")
        self.consumed_counter.incr()
        _logger.debug("SimpleConsume handling the task: %s...", task)
        try:
            result = self.consume(task)
        except Exception as error:
            _logger.exception(
                "SimpleConsume handling the task and got failed: %s...", error
            )
            raise error
        _logger.debug("SimpleConsume handled the task, result=%s...", result)

    def consume(self, task):
        """消费。"""
        _logger.debug("SimpleConsumer is handling the task: %s...", task)
        if self.consume_callback and callable(self.consume_callback):
            _logger.debug(
                "SimpleConsumer is calling consume_callback: args=%s kwargs=%s...",
                self.consume_callback_args,
                self.consume_callback_kwargs,
            )
            result = self.consume_callback(
                task, *self.consume_callback_args, **self.consume_callback_kwargs
            )
            _logger.debug("SimpleConsumer call consume_callback finished.")
        else:
            result = None
        _logger.debug("SimpleConsumer call consume_callback done, result: %s.", result)
        return result


class SimpleServer(object):
    """简易的服务器。"""

    def __init__(self, workers=None, **kwargs):
        workers = workers or []
        self.workers = [] + workers
        self.start_lock = threading.Lock()
        self.started = None
        self.started_time = None
        self.stop_flag = None
        self.stop_time = None
        self.terminate_flag = False
        self.terminate_time = None
        self.kwargs = kwargs

    def add_worker(self, worker):
        """添加服务。"""
        self.workers.append(worker)

    @property
    def is_running(self):
        """是否还在运行"""
        for worker in self.workers:
            if worker.is_running:
                return True
        return False

    @property
    def stopped(self):
        """是否已关停。"""
        for worker in self.workers:
            if not worker.stopped:
                return False
        return True

    @property
    def stopped_time(self):
        """关停时间。"""
        latest_time = None
        for worker in self.workers:
            if latest_time is None:
                latest_time = worker.stopped_time
            if worker.stopped_time > latest_time:
                latest_time = worker.stopped_time
        return latest_time

    @property
    def terminated(self):
        """是否已终止。"""
        for worker in self.workers:
            if not worker.terminated:
                return False
        return True

    @property
    def terminated_time(self):
        """终止时间。"""
        latest_time = None
        for worker in self.workers:
            if latest_time is None:
                latest_time = worker.terminated_time
            if worker.terminated_time > latest_time:
                latest_time = worker.terminated_time
        return latest_time

    def start(self):
        """启动服务。"""
        _logger.debug("SimpleServer starting...")
        with self.start_lock:
            self.stop_flag = False
            self.stop_time = None
            for worker in self.workers:
                _logger.info("SimpleServer starting worker: %s", worker.service_name)
                worker.start()
            if not self.started:
                self.started_time = time.time()
                self.started = True

    def stop(self, wait=True, wait_timeout=-1):
        """关停服务。允许再重启。"""
        _logger.debug("SimpleServer stopping...")
        self.stop_time = time.time()
        self.stop_flag = True
        results = []
        for worker in self.workers:
            result = worker.stop(wait, wait_timeout)
            results.append(result)
        for result in results:
            if result is None:
                _logger.debug("SimpleServer stopping result=None")
                return None
            if result is False:
                _logger.debug("SimpleServer stopping result=False")
                return False
        _logger.debug("SimpleServer stopping result=True")
        return True

    def terminate(self, wait=True, wait_timeout=-1):
        """终止服务。不允许再重启。"""
        _logger.debug("SimpleServer terminating...")
        self.terminate_time = time.time()
        self.terminate_flag = True
        results = []
        for worker in self.workers:
            result = worker.terminate(wait, wait_timeout)
        for result in results:
            if result is None:
                _logger.debug("SimpleServer terminating result=None")
                return None
            if result is False:
                _logger.debug("SimpleServer terminating result=False")
                return False
        _logger.debug("SimpleServer terminating result=True")
        return True

    def join(self, wait=True, wait_timeout=-1):
        """等待服务结束。"""
        _logger.debug("SimpleServer joining...")
        results = []
        for worker in self.workers:
            result = worker.join(wait, wait_timeout)
        for result in results:
            if result is None:
                _logger.debug("SimpleServer joining result=None")
                return None
            if result is False:
                _logger.debug("SimpleServer joining result=False")
                return False
        _logger.debug("SimpleServer joining result=True")
        return True

    @classmethod
    def serve(cls, **kwargs):
        """生产服务器，并启动。"""
        server = cls(**kwargs)
        server.start()
        return server


class SimpleProducerConsumerServer(SimpleServer):
    default_queue_size = 200
    default_producer_class = SimpleProducer
    default_consumer_class = SimpleConsumer
    default_producer_number = 1
    default_consumer_number = 1

    def __init__(
        self,
        producer_class=None,
        consumer_class=None,
        producer_number=None,
        consumer_number=None,
        queue_size=None,
        server=None,
        service_name=None,
        **kwargs
    ):
        self.producer_class = producer_class or self.default_producer_class
        self.consumer_class = consumer_class or self.default_consumer_class
        self.producer_number = producer_number or self.default_producer_number
        self.consumer_number = consumer_number or self.default_consumer_number
        self.kwargs = kwargs
        self.queue_size = queue_size or self.default_queue_size
        self.server = server
        self.service_name = service_name or self.__class__.__name__
        self.task_queue = Queue(self.queue_size)
        self.producers = self.create_producers()
        self.consumers = self.create_consumers()
        super(SimpleProducerConsumerServer, self).__init__(
            self.producers + self.consumers
        )

    def create_producers(self):
        _logger.info("SimpleProducerConsumerServer creating producers...")
        producers = []
        for index in range(self.producer_number):
            service_name = self.service_name + ":producer#{0}".format(index)
            _logger.info(
                "SimpleProducerConsumerServer creating producer: {0}".format(
                    service_name
                )
            )
            args = self.kwargs.get("producer_class_init_args", [])
            kwargs = {
                "task_queue": self.task_queue,
                "server": self,
                "service_name": service_name,
            }
            kwargs.update(self.kwargs.get("producer_class_init_kwargs", {}))
            kwargs.update(self.kwargs)
            producer = self.producer_class(*args, **kwargs)
            producers.append(producer)
        _logger.info("SimpleProducerConsumerServer creating producers done")
        return producers

    def create_consumers(self):
        _logger.info("SimpleProducerConsumerServer creating consumers...")
        consumers = []
        for index in range(self.consumer_number):
            service_name = self.service_name + ":consumer#{0}".format(index)
            _logger.info(
                "SimpleProducerConsumerServer creating consumer: {0}".format(
                    service_name
                )
            )
            args = self.kwargs.get("consumer_class_init_args", [])
            kwargs = {
                "task_queue": self.task_queue,
                "server": self,
                "service_name": service_name,
            }
            kwargs.update(self.kwargs.get("consumer_class_init_kwargs", {}))
            kwargs.update(self.kwargs)
            consumer = self.consumer_class(*args, **kwargs)
            consumers.append(consumer)
        _logger.info("SimpleProducerConsumerServer creating consumers done")
        return consumers


class JobExecuteTimeout(Exception):
    """20033, 任务执行超时"""


class JobResultNotSet(Exception):
    """20034, 任务结果未设置"""


class Future(object):
    """JobQueue运行结果。"""

    def __init__(self):
        # 结果是否已经生成信号
        self.event = threading.Event()
        # 结果是否成功。Job执行完成，没有抛出异常，则认为结果成功。
        self.success = None
        # 成功后的结果
        self.result = None
        # 失败后的异常
        self.error = None

    def wait(self, timeout):
        """登录结果。"""
        return self.event.wait(timeout=timeout)

    def set_result(self, result):
        """设置成功结果。"""
        self.success = True
        self.result = result
        self.error = None
        self.event.set()

    def set_error(self, error):
        """设置异常。"""
        self.success = False
        self.result = None
        self.error = error
        self.event.set()

    def get_result(self, timeout):
        """等待Job执行结束，并返回结果，如果有异常则抛出异常。"""
        if not self.wait(timeout):
            raise JobExecuteTimeout("job execute timeout...")
        if self.success is None:
            raise JobResultNotSet("job result not set")
        if self.success:
            return self.result
        else:
            raise self.error


class JobQueue(object):
    """任务队列。"""

    _JOB_QUEUE_GET_TIMEOUT = 1

    def __init__(self):
        self.job_queue = Queue()
        self.stop_flag = False
        self.worker_thread_counter = WorkerCounter()

    def async_execute(self, method, args=None, kwargs=None):
        """异步执行。返回Future对象。"""
        args = args or ()
        kwargs = kwargs or {}
        future = Future()
        self.job_queue.put((method, args, kwargs, future))
        return future

    def execute(self, method, args=None, kwargs=None, timeout=300):
        """同步执行。返回结果或抛出异常。"""
        future = self.async_execute(method, args, kwargs)
        return future.get_result(timeout)

    def serve_forever(self):
        """启动服务。可以在不同的工作线程中多次启动。"""
        self.stop_flag = False
        self.worker_thread_counter.incr()
        try:
            while not self.stop_flag:
                try:
                    method, args, kwargs, future = self.job_queue.get(
                        timeout=self._JOB_QUEUE_GET_TIMEOUT
                    )
                except Empty:
                    continue
                try:
                    args = args or ()
                    kwargs = kwargs or {}
                    result = method(*args, **kwargs)
                    future.set_result(result)
                except Exception as error:
                    future.set_error(error)
        finally:
            self.worker_thread_counter.decr()

    def stop(self, timeout=None):
        """停止所有服务。"""
        self.stop_flag = True
        return self.worker_thread_counter.wait(timeout)


class IdleReportor(object):
    """工作线程长时间空闲报告器。

    每隔{report_interval}秒输出一次空闲报告。
    如果这段时间内有一个任务被处理，则忽略从最后一个任何开始重新计算空闲时长。

    @param report_interval: int
    @param worker_name: str
    @param report: callable, optional.

        ```
            def report(info : str) -> None:
                pass
        ```

        一般传入调用处的_logger.info函数即可。
        如果不传的话，则使用当前模块的_logger.info函数，可能不便于调试，建议传到调用者所在模块的_logger.info。

    """

    def __init__(self, report_interval, worker_name, report=None):
        self.report_interval = report_interval
        self.worker_name = worker_name
        self.idle_start_time = None
        self.idle_loop_time = None
        self.report = report or _logger.info

    def idle(self, nowtime=None):
        """在工作线程空闲时调用本函数。"""
        if nowtime is None:
            nowtime = time.time()
        if self.idle_start_time is None:
            self.idle_start_time = nowtime
        if self.idle_loop_time is None:
            self.idle_loop_time = nowtime
        if nowtime - self.idle_loop_time > self.report_interval:
            self.idle_loop_time = nowtime
            self.do_report(nowtime)

    def work(self):
        """在工作线程有任务前调用本函数。"""
        if not self.idle_start_time is None:
            self.idle_start_time = None
            self.idle_loop_time = None

    def get_report_info(self, idle_seconds):
        """生成空闲报告信息。"""
        # pylint: disable=consider-using-f-string
        return "{0} has NOT received a new event for {1} seconds...".format(
            self.worker_name,
            idle_seconds,
        )

    def do_report(self, nowtime=None):
        """输出工作线程空闲报告。"""
        if nowtime is None:
            nowtime = time.time()
        idle_seconds = int(nowtime - self.idle_start_time)
        self.report(self.get_report_info(idle_seconds))
