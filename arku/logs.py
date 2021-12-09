from typing import Any, Dict


def default_log_config(verbose: bool) -> Dict[str, Any]:
    """
    Setup default config. for dictConfig.

    :param verbose: level: DEBUG if True, INFO if False
    :return: dict suitable for ``logging.config.dictConfig``
    """
    log_level = 'DEBUG' if verbose else 'INFO'
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'arku.standard': {'level': log_level, 'class': 'logging.StreamHandler', 'formatter': 'arku.standard'}
        },
        'formatters': {'arku.standard': {'format': '%(asctime)s: %(message)s', 'datefmt': '%H:%M:%S'}},
        'loggers': {'arku': {'handlers': ['arku.standard'], 'level': log_level}},
    }
