import json
import pathlib

import requests
import pytest

import youtube_monitor_action

CWD = pathlib.Path()
FILE_DIR = pathlib.Path(__file__).parent
TESTS_DIR = FILE_DIR / "response_test_cases"


@pytest.mark.parametrize(
    "input_file", [file for file in TESTS_DIR.iterdir() if file.is_file()]
)
def test__example_response__yields_expected(input_file, snapshot, mocker):
    mock = mocker.patch.object(requests, "get")
    mock.return_value.content = input_file.read_text()

    result = youtube_monitor_action.__main__._get_channel_data("foo")

    snapshot.assert_match(json.dumps(result, indent=4), "expected.json")
