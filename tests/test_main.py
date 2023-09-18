import asyncio
import dataclasses
import functools
import logging
from collections import Counter
from datetime import datetime, timezone
from random import shuffle
from time import time

import dirty_equals
import msgpack
import pytest

from arku.connections import ArkuRedis
from arku.constants import default_queue_name
from arku.jobs import Job, JobDef, SerializationError
from arku.utils import timestamp_ms
from arku.worker import Retry, Worker, func


async def test_enqueue_job(arku_redis: ArkuRedis, worker):
    async def foobar(ctx):
        return 42

    j = await arku_redis.enqueue_job('foobar')
    worker: Worker = worker(functions=[func(foobar, name='foobar')])
    await worker.main()
    r = await j.result(poll_delay=0)
    assert r == 42  # 1


async def test_enqueue_job_different_queues(arku_redis: ArkuRedis, worker):
    async def foobar(ctx):
        return 42

    j1 = await arku_redis.enqueue_job('foobar', _queue_name='arku:queue1')
    j2 = await arku_redis.enqueue_job('foobar', _queue_name='arku:queue2')
    worker1: Worker = worker(functions=[func(foobar, name='foobar')], queue_name='arku:queue1')
    worker2: Worker = worker(functions=[func(foobar, name='foobar')], queue_name='arku:queue2')

    await worker1.main()
    await worker2.main()
    r1 = await j1.result(poll_delay=0)
    r2 = await j2.result(poll_delay=0)
    assert r1 == 42  # 1
    assert r2 == 42  # 2


async def test_enqueue_job_nested(arku_redis: ArkuRedis, worker):
    async def foobar(ctx):
        return 42

    async def parent_job(ctx):
        inner_job = await ctx['redis'].enqueue_job('foobar')
        return inner_job.job_id

    job = await arku_redis.enqueue_job('parent_job')
    worker: Worker = worker(functions=[func(parent_job, name='parent_job'), func(foobar, name='foobar')])

    await worker.main()
    result = await job.result(poll_delay=0)
    assert result is not None
    inner_job = Job(result, arku_redis)
    inner_result = await inner_job.result(poll_delay=0)
    assert inner_result == 42


async def test_enqueue_job_nested_custom_serializer(arku_redis_msgpack: ArkuRedis, worker):
    async def foobar(ctx):
        return 42

    async def parent_job(ctx):
        inner_job = await ctx['redis'].enqueue_job('foobar')
        return inner_job.job_id

    job = await arku_redis_msgpack.enqueue_job('parent_job')

    worker: Worker = worker(
        functions=[func(parent_job, name='parent_job'), func(foobar, name='foobar')],
        arku_redis=None,
        job_serializer=msgpack.packb,
        job_deserializer=functools.partial(msgpack.unpackb, raw=False),
    )

    await worker.main()
    result = await job.result(poll_delay=0)
    assert result is not None
    inner_job = Job(result, arku_redis_msgpack, _deserializer=functools.partial(msgpack.unpackb, raw=False))
    inner_result = await inner_job.result(poll_delay=0)
    assert inner_result == 42


async def test_enqueue_job_custom_queue(arku_redis: ArkuRedis, worker):
    async def foobar(ctx):
        return 42

    async def parent_job(ctx):
        inner_job = await ctx['redis'].enqueue_job('foobar')
        return inner_job.job_id

    job = await arku_redis.enqueue_job('parent_job', _queue_name='spanner')

    worker: Worker = worker(
        functions=[func(parent_job, name='parent_job'), func(foobar, name='foobar')],
        arku_redis=None,
        queue_name='spanner',
    )

    await worker.main()
    inner_job_id = await job.result(poll_delay=0)
    assert inner_job_id is not None
    inner_job = Job(inner_job_id, arku_redis, _queue_name='spanner')
    inner_result = await inner_job.result(poll_delay=0)
    assert inner_result == 42


async def test_job_error(arku_redis: ArkuRedis, worker):
    async def foobar(ctx):
        raise RuntimeError('foobar error')

    j = await arku_redis.enqueue_job('foobar')
    worker: Worker = worker(functions=[func(foobar, name='foobar')])
    await worker.main()

    with pytest.raises(RuntimeError, match='foobar error'):
        await j.result(poll_delay=0)


async def test_job_info(arku_redis: ArkuRedis):
    t_before = time()
    j = await arku_redis.enqueue_job('foobar', 123, a=456)
    info = await j.info()
    assert info.enqueue_time == dirty_equals.IsNow(tz=timezone.utc)
    assert info.job_try is None
    assert info.function == 'foobar'
    assert info.args == (123,)
    assert info.kwargs == {'a': 456}
    assert abs(t_before * 1000 - info.score) < 1000


async def test_repeat_job(arku_redis: ArkuRedis):
    j1 = await arku_redis.enqueue_job('foobar', _job_id='job_id')
    assert isinstance(j1, Job)
    j2 = await arku_redis.enqueue_job('foobar', _job_id='job_id')
    assert j2 is None


async def test_defer_until(arku_redis: ArkuRedis):
    j1 = await arku_redis.enqueue_job(
        'foobar',
        _job_id='job_id',
        _defer_until=datetime(2032, 1, 1, tzinfo=timezone.utc),
    )
    assert isinstance(j1, Job)
    score = await arku_redis.zscore(default_queue_name, 'job_id')
    assert score == 1_956_528_000_000


async def test_defer_by(arku_redis: ArkuRedis):
    j1 = await arku_redis.enqueue_job('foobar', _job_id='job_id', _defer_by=20)
    assert isinstance(j1, Job)
    score = await arku_redis.zscore(default_queue_name, 'job_id')
    ts = timestamp_ms()
    assert score > ts + 19000
    assert ts + 21000 > score


async def test_mung(arku_redis: ArkuRedis, worker):
    """
    check a job can't be enqueued multiple times with the same id
    """
    counter = Counter()

    async def count(ctx, v):
        counter[v] += 1

    tasks = []
    for i in range(50):
        tasks.extend(
            [
                arku_redis.enqueue_job('count', i, _job_id=f'v-{i}'),
                arku_redis.enqueue_job('count', i, _job_id=f'v-{i}'),
            ]
        )
    shuffle(tasks)
    await asyncio.gather(*tasks)

    worker: Worker = worker(functions=[func(count, name='count')])
    await worker.main()
    assert counter.most_common(1)[0][1] == 1  # no job go enqueued twice


async def test_custom_try(arku_redis: ArkuRedis, worker):
    async def foobar(ctx):
        return ctx['job_try']

    j1 = await arku_redis.enqueue_job('foobar')
    w: Worker = worker(functions=[func(foobar, name='foobar')])
    await w.main()
    r = await j1.result(poll_delay=0)
    assert r == 1

    j2 = await arku_redis.enqueue_job('foobar', _job_try=3)
    await w.main()
    r = await j2.result(poll_delay=0)
    assert r == 3


async def test_custom_try2(arku_redis: ArkuRedis, worker):
    async def foobar(ctx):
        if ctx['job_try'] == 3:
            raise Retry()
        return ctx['job_try']

    j1 = await arku_redis.enqueue_job('foobar', _job_try=3)
    w: Worker = worker(functions=[func(foobar, name='foobar')])
    await w.main()
    r = await j1.result(poll_delay=0)
    assert r == 4


async def test_cant_pickle_arg(arku_redis: ArkuRedis, worker):
    class Foobar:
        def __getstate__(self):
            raise TypeError("this doesn't pickle")

    with pytest.raises(SerializationError, match='unable to serialize job "foobar"'):
        await arku_redis.enqueue_job('foobar', Foobar())


async def test_cant_pickle_result(arku_redis: ArkuRedis, worker):
    class Foobar:
        def __getstate__(self):
            raise TypeError("this doesn't pickle")

    async def foobar(ctx):
        return Foobar()

    j1 = await arku_redis.enqueue_job('foobar')
    w: Worker = worker(functions=[func(foobar, name='foobar')])
    await w.main()
    with pytest.raises(SerializationError, match='unable to serialize result'):
        await j1.result(poll_delay=0)


async def test_get_jobs(arku_redis: ArkuRedis):
    await arku_redis.enqueue_job('foobar', a=1, b=2, c=3)
    await asyncio.sleep(0.01)
    await arku_redis.enqueue_job('second', 4, b=5, c=6)
    await asyncio.sleep(0.01)
    await arku_redis.enqueue_job('third', 7, b=8)
    jobs = await arku_redis.queued_jobs()
    assert [dataclasses.asdict(j) for j in jobs] == [
        {
            'function': 'foobar',
            'args': (),
            'kwargs': {'a': 1, 'b': 2, 'c': 3},
            'job_try': None,
            'enqueue_time': dirty_equals.IsNow(tz=timezone.utc),
            'score': dirty_equals.IsInt,
        },
        {
            'function': 'second',
            'args': (4,),
            'kwargs': {'b': 5, 'c': 6},
            'job_try': None,
            'enqueue_time': dirty_equals.IsNow(tz=timezone.utc),
            'score': dirty_equals.IsInt,
        },
        {
            'function': 'third',
            'args': (7,),
            'kwargs': {'b': 8},
            'job_try': None,
            'enqueue_time': dirty_equals.IsNow(tz=timezone.utc),
            'score': dirty_equals.IsInt,
        },
    ]
    assert jobs[0].score < jobs[1].score < jobs[2].score
    assert isinstance(jobs[0], JobDef)
    assert isinstance(jobs[1], JobDef)
    assert isinstance(jobs[2], JobDef)


async def test_enqueue_multiple(arku_redis: ArkuRedis, caplog):
    caplog.set_level(logging.DEBUG)
    results = await asyncio.gather(*[arku_redis.enqueue_job('foobar', i, _job_id='testing') for i in range(10)])
    assert sum(r is not None for r in results) == 1
    assert sum(r is None for r in results) == 9
    assert 'WatchVariableError' not in caplog.text
