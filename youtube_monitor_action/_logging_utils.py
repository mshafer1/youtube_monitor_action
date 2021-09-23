import logging
import logging.handlers
import pathlib
from typing import List, NamedTuple, Union


class LogFileSetup(NamedTuple):
    """Logging settings for file handler."""

    path: pathlib.Path
    logging_level: int
    format: Union[None, str]
    size: int
    days: int
    backups: int


MAX_LEVEL_WIDTH = len("WARNING")
DEFAULT_LONG_FORMAT = (
    f"%(asctime)s  %(levelname)-{MAX_LEVEL_WIDTH}s  %(filename)s.%(funcName)s : %(message)s"
)

DEFAULT_SHORT_FORMAT = f"%(asctime)s  %(levelname)-{MAX_LEVEL_WIDTH}s   %(message)s"


def configure_module_logger(
    logger: logging.Logger,
    main_logging_level: int,
    main_format: str = DEFAULT_SHORT_FORMAT,
    file_handler_infos: List[LogFileSetup] = [],
) -> None:
    """Configure logger handlers."""
    main_formatter = logging.Formatter(main_format)
    logger.setLevel(logging.DEBUG)  # have to be set at max

    main_handler = logging.StreamHandler()
    main_handler.setFormatter(main_formatter)
    main_handler.setLevel(main_logging_level)
    logger.addHandler(main_handler)

    for file_setting in file_handler_infos:
        invalid_config_error_msg = (
            f"Error: file logger must have exactly one positive value"
            f" for either days or size (recieved {file_setting.days}, and {file_setting.size})"
        )
        if not (bool(file_setting.days < 0) ^ bool(file_setting.size < 0)):
            raise Exception(invalid_config_error_msg)

        file_setting.path.parent.mkdir(parents=True, exist_ok=True)

        if file_setting.days > 0:
            file_handler = logging.handlers.TimedRotatingFileHandler(
                filename=str(file_setting.path),
                when="D",
                interval=file_setting.days,
                backupCount=file_setting.backups,
            )
        elif file_setting.size > 0:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=str(file_setting.path),
                maxBytes=file_setting.size,
                backupCount=file_setting.backups,
            )

        file_handler.setLevel(file_setting.logging_level)
        _formatter = logging.Formatter(fmt=file_setting.format or DEFAULT_LONG_FORMAT)
        file_handler.setFormatter(_formatter)
        logger.addHandler(file_handler)
