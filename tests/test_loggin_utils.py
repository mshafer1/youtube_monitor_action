import logging
import re

import pytest

import youtube_monitor_action.__main__


@pytest.fixture()
def _setup_logger(mocker, tmp_path):
    logger = logging.getLogger("test_logger")
    mocker.patch.object(youtube_monitor_action.__main__, "_MODULE_LOGGER", logger)
    youtube_monitor_action.__main__._setup_logger(
        main_logging_level=logging.INFO, log_file=tmp_path / "logs" / "log.txt"
    )

    yield logger


@pytest.mark.parametrize(
    "logging_level,file,expected",
    [
        (logging.INFO, "log.txt", True),
        (logging.DEBUG, "log.txt", True),
    ],
)
def test_level_puts_message_where_expected(
    logging_level, file, expected, tmp_path, _setup_logger: logging.Logger
):
    # _setup_logger.debug("test")
    _setup_logger.log(logging_level, "Bacon Ipsum")

    logged = (tmp_path / "logs" / file).read_text()

    assert (
        "Bacon Ipsum" in logged
    ) == expected, (
        f"Error, logging was{'' if expected else ' NOT'} expected to be in {file}"
    )
    assert logged.split().count("Bacon") == (
        1 if expected else 0
    ), f"Error, logging was{'' if expected else ' NOT'} expected exactly once"


@pytest.mark.parametrize(
    "logging_level,expected",
    [
        (logging.INFO, True),
        (logging.WARNING, True),
        (logging.CRITICAL, True),
        (logging.DEBUG, False),
    ],
)
def test_level_puts_message_in_output_when_expected(
    logging_level, expected, capture_stderr, capture_stdout, _setup_logger: logging.Logger
):
    _setup_logger.log(logging_level, "Bacon Ipsum")

    output = capture_stderr.getvalue()
    stdout = capture_stdout.getvalue()

    assert not stdout

    assert (
        "Bacon Ipsum" in output
    ) == expected, (
        f"Error, logging was{'' if expected else ' NOT'} expected to be in stderr"
    )
    assert re.split(r"\s|\:", output).count("Bacon") == (
        1 if expected else 0
    ), f"Error, logging was{'' if expected else ' NOT'} expected exactly once"

