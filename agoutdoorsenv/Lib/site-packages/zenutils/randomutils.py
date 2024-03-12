#!/usr/bin/env python
# -*- coding: utf8 -*-
"""随机数工具。"""
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
    "choices",
    "get_password_seed32",
    "Random",
    "Lcg31Random",
    "UuidGenerator",
    "uuid1",
    "uuid3",
    "uuid4",
    "uuid5",
]

import random
import time
import uuid
import socket
import getpass
import os
import threading
import hashlib
import struct
import functools

if not hasattr(time, "perf_counter"):  # fix for py2.7
    time.perf_counter = time.clock

DEFAULT_MODULUS = (2**30 - 123) * 0.91  # always NOT change this
DEFAULT_MULTIPLIER = (2**29 - 456) * 0.93  # always NOT change this
DEFAULT_INCREMENT = (2**28 - 789) * 0.95  # always NOT change this

LCG31_RANDOM_DEFAULT_MODULUS = 2**31
LCG31_RANDOM_DEFAULT_MULTIPLIER = 1103515245
LCG31_RANDOM_DEFAULT_INCREMENT = 12345


def get_password_seed32(passowrd=None):
    """Turn password to int32 seed value.

    password can be None, str, bytes, int, long typed.
    """
    modulus = 2**32
    if passowrd is None:
        return int(time.time()) % modulus
    if isinstance(passowrd, NUMERIC_TYPES):
        return int(passowrd) % modulus
    if isinstance(passowrd, float):
        return int(passowrd) % modulus
    if isinstance(passowrd, STR_TYPE):
        passowrd = passowrd.encode("utf-8")
    if isinstance(passowrd, BYTES_TYPE):
        from zlib import crc32

        return crc32(passowrd) % modulus
    else:
        msg = "Random seed type must be in (str, bytes, int, long, float), but {} got.".format(
            type(passowrd)
        )
        raise ValueError(msg)


class RandomBase(object):
    """Pseudo-random generator base."""

    def __init__(self, seed=None, **kwrags):
        self.seed = self.get_seed(seed, **kwrags)

    @classmethod
    def get_seed(cls, seed, **kwargs):
        return get_password_seed32(seed)

    def random(self):
        """return a float number in [0, 1)."""
        raise NotImplementedError()

    def randint(self, a, b=None):
        """If a<b, then return int number in [a, b). If a>b, then return int number in [b, a)."""
        if b is None:
            return int(self.random() * a)
        else:
            if a > b:
                a, b = b, a
            return int(self.random() * (b - a) + a)

    def get_bytes(self, length=1):
        return bytes(bytearray([self.randint(256) for _ in range(length)]))

    def choice(self, seq):
        index = self.randint(len(seq))
        return seq[index]

    def choices(self, population, k=1):
        result = []
        for _ in range(k):
            result.append(self.choice(population))
        return result

    def shuffle(self, thelist, x=2):
        length = len(thelist)
        if not isinstance(thelist, list):
            thelist = list(thelist)
        for _ in range(int(length * x)):
            p = self.randint(length)
            q = self.randint(length)
            if p == q:
                q += self.randint(length)
                q %= length
            thelist[p], thelist[q] = thelist[q], thelist[p]
        return thelist


class Random(RandomBase):
    """Pseudo-random number generator. Linear congruential generator.

    ## randomness testing

    import os
    import random
    from fastutils import randomutils

    def test1(length):
        data = set()
        while True:
            bs = os.urandom(length)
            if bs in data:
                return "os.urandom({})={}".format(length, len(data))
            data.add(bs)

    def test2(length):
        data = set()
        while True:
            bs = random.randbytes(length)
            if bs in data:
                return "random.randbytes({})={}".format(length, len(data))
            data.add(bs)

    def test3(length):
        data = set()
        rnd = randomutils.Random()
        while True:
            bs = rnd.get_bytes(length)
            if bs in data:
                return "randomutils.Random({})={}".format(length, len(data))
            data.add(bs)

    print(test1(1))
    print(test1(2))
    print(test1(3))
    print(test1(4))
    print(test1(5))
    print(test1(6))

    print(test2(1))
    print(test2(2))
    print(test2(3))
    print(test2(4))
    print(test2(5))
    print(test2(6))

    print(test3(1))
    print(test3(2))
    print(test3(3))
    print(test3(4))
    print(test3(5))
    print(test3(6))

    ## randomness testing result

    os.urandom(1)=13
    os.urandom(2)=583
    os.urandom(3)=3245
    os.urandom(4)=51189
    os.urandom(5)=1280810
    os.urandom(6)=33771127               # good, always about 35,000,000
    random.randbytes(1)=2
    random.randbytes(2)=347
    random.randbytes(3)=1274
    random.randbytes(4)=66322
    random.randbytes(5)=1060238
    random.randbytes(6)=38210136         # good, always about 38,000,000
    randomutils.Random(1)=6
    randomutils.Random(2)=80
    randomutils.Random(3)=53
    randomutils.Random(4)=98189
    randomutils.Random(5)=1097420
    randomutils.Random(6)=10117127       # not so good, about 5,000,000 ~ 10,000,000

    """

    def __init__(
        self, seed=None, a=DEFAULT_MULTIPLIER, c=DEFAULT_INCREMENT, m=DEFAULT_MODULUS
    ):
        self.seed = self.get_seed(seed)
        self.a = a
        self.c = c
        self.m = m

    @classmethod
    def get_seed(cls, seed):
        from zenutils import numericutils

        if seed is None:
            return time.time()
        if isinstance(seed, STR_TYPE):
            seed = seed.encode("utf-8")
        if isinstance(seed, BYTES_TYPE):
            seed = numericutils.from_bytes(hashlib.sha512(seed).digest(), "big")
        if isinstance(seed, NUMERIC_TYPES):
            return seed
        else:
            msg = "Random seed type must be in (str, bytes, int, long, float), but {} got.".format(
                type(seed)
            )
            raise ValueError(msg)

    def random(self):
        """return a float number in [0, 1)."""
        r = (self.a * self.seed + self.c) % self.m
        p = r / self.m
        self.seed = r
        return p


class Lcg31Random(RandomBase):
    """Linear congruential generator.

    Using modulus=2**31, multiplier=1103515245, increment=12345
    """

    def __init__(
        self,
        seed=None,
        a=LCG31_RANDOM_DEFAULT_MULTIPLIER,
        c=LCG31_RANDOM_DEFAULT_INCREMENT,
        m=LCG31_RANDOM_DEFAULT_MODULUS,
    ):
        self.a = a
        self.c = c
        self.m = m
        self.seed = self.get_seed(seed)

    @classmethod
    def get_seed(cls, seed):
        return get_password_seed32(seed)

    def random(self):
        r = (self.a * self.seed + self.c) % self.m
        p = r / self.m
        self.seed = r
        return p


class HashPrng(RandomBase):
    BASE_BYTES = 4
    BASE = 256**BASE_BYTES

    def __init__(self, seed=None, method=hashlib.sha512):
        self.seed = self.get_seed(seed, method)
        self.generator = method(self.seed)
        self.digests = []
        self.round = 1

    @classmethod
    def get_seed(cls, seed, method):
        if seed is None:
            seed = time.time()
        seed = force_bytes(seed)
        return method(seed).digest()

    def random(self):
        if not self.digests:
            self.round += 1
            self.generator.update(force_bytes(self.round))
            self.generator.update(self.seed)
            digest_data = self.generator.digest()
            digest_count = len(digest_data) // 4
            self.digests = list(struct.unpack(">" + ("I" * digest_count), digest_data))
        digest = self.digests.pop()
        result = 1.0 * digest / self.BASE
        return result


def get_random_space_size(generator, length):
    data = set()
    while True:
        seed = generator.get_bytes(length)
        if seed in data:
            return len(data)
        data.add(seed)


class UuidGenerator(object):
    """UUID generator, using machine based counter, so that it will NOT generate conflict UUIDs."""

    def __init__(self, namespace=None):
        from zenutils import sysutils
        from zenutils import strutils

        self.namespace = strutils.force_text(namespace or "default")
        self.seed1 = strutils.force_text(uuid.uuid1())
        self.seed4 = strutils.force_text(uuid.uuid4())
        self.hostname = strutils.force_text(socket.gethostname())
        self.node = strutils.force_text(uuid.getnode())
        self.user = strutils.force_text(getpass.getuser())
        self.pid = strutils.force_text(os.getpid())
        self.tid = strutils.force_text(sysutils.get_current_thread_id())
        self.counter = 0
        self.counter_lock = threading.Lock()
        self.domain_template = ".".join(
            [
                "{ts1}",
                "{ts2}",
                "{counter}",
                self.tid,
                self.pid,
                self.user,
                self.node,
                self.hostname,
                self.seed4,
                self.seed1,
                self.namespace,
            ]
        )
        self.ts0 = time.perf_counter()

    def next(self, n=1):
        from zenutils import strutils

        if n < 1:
            return []
        with self.counter_lock:
            counter_start = self.counter
            self.counter += n
            counter_end = self.counter
        uuids = []
        for counter in range(counter_start, counter_end):
            ts1 = int(time.time() * 1000000)
            ts2 = int(time.perf_counter() * 1000000000)
            domain = self.domain_template.format(ts1=ts1, ts2=ts2, counter=counter)
            new_uuid = uuid.UUID(
                bytes=hashlib.md5(
                    uuid.NAMESPACE_DNS.bytes + strutils.force_bytes(domain)
                ).digest()
            )
            uuids.append(new_uuid)
        if n == 1:
            return uuids[0]
        else:
            return uuids


uuidgen = UuidGenerator()


def uuid1():
    return uuidgen.next()


uuid3 = uuid4 = uuid5 = uuid1


def choices(thelist, k):
    """Randomly select k elements from thelist. Element can be selected multiple times.

    @Returns:
        (list): Returns selected k elements.

    @Parameters:
        thelist(list of Any): The list where the elements select from.
        k(int): Select K times.

    @Examples:
        randomutils.choices([1,2,3], 2) --> Result may [1, 1], [1, 2], [1,3], [2, 1], [2, 2]...
        randomutils.choices('hello', 2) --> Result may ['h', 'e'], ['h', 'o']...
    """
    return [random.choice(thelist) for _ in range(k)]


Md5Prng = functools.partial(HashPrng, method=hashlib.md5)
ShaPrng = functools.partial(HashPrng, method=hashlib.sha1)
Sha1Prng = functools.partial(HashPrng, method=hashlib.sha1)
Sha224Prng = functools.partial(HashPrng, method=hashlib.sha224)
Sha256Prng = functools.partial(HashPrng, method=hashlib.sha256)
Sha384Prng = functools.partial(HashPrng, method=hashlib.sha384)
Sha512Prng = functools.partial(HashPrng, method=hashlib.sha512)
