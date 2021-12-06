import importlib.metadata

from click.testing import CliRunner

import arq.cli


async def foobar(ctx):
    return 42


class WorkerSettings:
    burst = True
    functions = [foobar]


def test__get_version(mocker):
    mocker.patch('importlib.metadata.version').return_value = 'v0.0.1b1'

    assert arq.cli._get_version() == 'v0.0.1b1'
    importlib.metadata.version.assert_called_once_with('arq')


def test__get_version_package_does_not_exist(mocker):
    mocker.patch(
        'importlib.metadata.version',
    ).side_effect = importlib.metadata.PackageNotFoundError

    assert arq.cli._get_version() == 'unknown'
    importlib.metadata.version.assert_called_once_with('arq')


def test_help():
    runner = CliRunner()
    result = runner.invoke(arq.cli.cli, ['--help'])
    assert result.exit_code == 0
    assert result.output.startswith('Usage: arq [OPTIONS] WORKER_SETTINGS\n')


def test_run():
    runner = CliRunner()
    result = runner.invoke(arq.cli.cli, ['tests.test_cli.WorkerSettings'])
    assert result.exit_code == 0
    assert 'Starting worker for 1 functions: foobar' in result.output


def test_check():
    runner = CliRunner()
    result = runner.invoke(arq.cli.cli, ['tests.test_cli.WorkerSettings', '--check'])
    assert result.exit_code == 1
    assert 'Health check failed: no health check sentinel value found' in result.output


async def mock_awatch():
    yield [1]


def test_run_watch(mocker):
    mocker.patch('watchgod.awatch', return_value=mock_awatch())
    runner = CliRunner()
    result = runner.invoke(arq.cli.cli, ['tests.test_cli.WorkerSettings', '--watch', 'tests'])
    assert result.exit_code == 0
    assert '1 files changes, reloading arq worker...'
