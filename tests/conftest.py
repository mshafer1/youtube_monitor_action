import io
from contextlib import redirect_stdout, redirect_stderr

import pytest

import youtube_monitor_action.__main__


@pytest.fixture(autouse=True)
def _log_to_temp_dir(mocker, tmp_path):
    log_dir = tmp_path / "logs"
    mocker.patch.object(youtube_monitor_action.__main__, "LOGGING_DIR", log_dir)
    yield


@pytest.fixture()
def capture_stdout():
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        yield stdout


@pytest.fixture()
def capture_stderr():
    stderr = io.StringIO()
    with redirect_stderr(stderr):
        yield stderr
