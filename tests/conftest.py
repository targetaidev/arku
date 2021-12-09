import asyncio
import functools

import msgpack
import pytest

from arku.connections import ArkuRedis, create_pool
from arku.worker import Worker


@pytest.yield_fixture
async def arku_redis(loop):
    redis_ = ArkuRedis(
        host='localhost',
        port=6379,
        encoding='utf-8',
    )
    await redis_.flushall()
    yield redis_
    await redis_.close()


@pytest.yield_fixture
async def arku_redis_msgpack(loop):
    redis_ = ArkuRedis(
        host='localhost',
        port=6379,
        encoding='utf-8',
        job_serializer=msgpack.packb,
        job_deserializer=functools.partial(msgpack.unpackb, raw=False),
    )
    await redis_.flushall()
    yield redis_
    await redis_.close()


@pytest.yield_fixture
async def worker(arku_redis):
    worker_: Worker = None

    def create(functions=[], burst=True, poll_delay=0, max_jobs=10, arku_redis=arku_redis, **kwargs):
        nonlocal worker_
        worker_ = Worker(
            functions=functions, redis_pool=arku_redis, burst=burst, poll_delay=poll_delay, max_jobs=max_jobs, **kwargs
        )
        return worker_

    yield create

    if worker_:
        await worker_.close()


@pytest.fixture(name='create_pool')
async def fix_create_pool(loop):
    pools = []

    async def create_pool_(settings, *args, **kwargs):
        pool = await create_pool(settings, *args, **kwargs)
        pools.append(pool)
        return pool

    yield create_pool_

    await asyncio.gather(*[p.close() for p in pools])
