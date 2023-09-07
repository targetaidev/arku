import logging
import os
import re
from dataclasses import dataclass
from datetime import timedelta

import pytest

import arku.typing
import arku.utils
from arku.connections import RedisSettings, log_redis_info


def test_settings_changed():
    settings = RedisSettings(port=123)
    assert settings.port == 123
    assert (
        "RedisSettings(host='localhost', port=123, database=0, password=None, ssl=None, conn_timeout=1, "
        "conn_retries=5, conn_retry_delay=1, sentinel=False, sentinel_master='mymaster')"
    ) == str(settings)


@pytest.mark.skip
async def test_redis_timeout(mocker, create_pool):
    mocker.spy(arku.utils.asyncio, 'sleep')
    with pytest.raises(OSError):
        await create_pool(RedisSettings(port=0, conn_retry_delay=0))
    assert arku.utils.asyncio.sleep.call_count == 5


@pytest.mark.skip
async def test_redis_sentinel_failure(create_pool):
    """
    FIXME: this is currently causing 3 "Task was destroyed but it is pending!" warnings
    """
    settings = RedisSettings()
    settings.host = [('localhost', 6379), ('localhost', 6379)]
    settings.sentinel = True
    try:
        pool = await create_pool(settings)
        await pool.ping('ping')
    except Exception as e:
        assert 'unknown command `SENTINEL`' in str(e)


async def test_redis_success_log(caplog, create_pool):
    caplog.set_level(logging.INFO)
    settings = RedisSettings()
    pool = await create_pool(settings)
    assert 'redis connection successful' not in [r.message for r in caplog.records]
    await pool.close()

    pool = await create_pool(settings, retry=1)
    assert 'redis connection successful' in [r.message for r in caplog.records]
    await pool.close()


async def test_redis_log(create_pool):
    redis = await create_pool(RedisSettings())
    await redis.flushall()
    await redis.set(b'a', b'1')
    await redis.set(b'b', b'2')

    log_msgs = []

    def _log(s):
        log_msgs.append(s)

    await log_redis_info(redis, _log)
    assert len(log_msgs) == 1
    assert re.search(r'redis_version=\d\.', log_msgs[0]), log_msgs
    assert log_msgs[0].endswith(' db_keys=2')


def test_truncate():
    assert arku.utils.truncate('123456', 4) == '123…'


def test_args_to_string():
    assert arku.utils.args_to_string((), {'d': 4}) == 'd=4'
    assert arku.utils.args_to_string((1, 2, 3), {}) == '1, 2, 3'
    assert arku.utils.args_to_string((1, 2, 3), {'d': 4}) == '1, 2, 3, d=4'


@pytest.mark.parametrize(
    'input,output', [(timedelta(days=1), 86_400_000), (42, 42000), (42.123, 42123), (42.123_987, 42124), (None, None)]
)
def test_to_ms(input, output):
    assert arku.utils.to_ms(input) == output


@pytest.mark.parametrize('input,output', [(timedelta(days=1), 86400), (42, 42), (42.123, 42.123), (None, None)])
def test_to_seconds(input, output):
    assert arku.utils.to_seconds(input) == output


def test_typing():
    assert 'OptionType' in arku.typing.__all__


def test_import_module():
    assert arku.utils.import_string('os.path') == os.path


def test_import_module_invalid():
    with pytest.raises(ImportError) as exc_info:
        arku.utils.import_string('xx')

    assert exc_info.value.args[0] == '"xx" doesn\'t look like a module path'


def test_import_no_attr():
    with pytest.raises(ImportError) as exc_info:
        arku.utils.import_string('os.foobar')

    assert exc_info.value.args[0] == 'Module "os" does not define a "foobar" attribute'


def test_redis_settings_validation():
    @dataclass
    class Settings:
        redis_settings: RedisSettings

    s1 = Settings(redis_settings=RedisSettings.from_dsn('redis://foobar:123/4'))
    assert s1.redis_settings.host == 'foobar'
    assert s1.redis_settings.host == 'foobar'
    assert s1.redis_settings.port == 123
    assert s1.redis_settings.database == 4
    assert s1.redis_settings.ssl is False

    s2 = Settings(redis_settings=RedisSettings(host='testing.com'))
    assert s2.redis_settings.host == 'testing.com'
    assert s2.redis_settings.port == 6379

    s3 = Settings(redis_settings=RedisSettings(ssl=True))
    assert s3.redis_settings.host == 'localhost'
    assert s3.redis_settings.ssl is True
