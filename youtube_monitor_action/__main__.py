import argparse
import logging
import os
import sys
import textwrap
import time
import typing
import pathlib

import yaml
import requests
import xmltodict

_MODULE_LOGGER = logging.getLogger(__name__)
CWD = pathlib.Path()
MODULE_DIR = pathlib.Path(__file__).parent
USER_DIR = pathlib.Path(os.path.expanduser("~"))  # OS agnostic way of getting user home
CONFIG_FILE = USER_DIR / ".config" / "youtube_monitor_action" / "config.yaml"


class _Options(typing.NamedTuple):
    n: int
    channel: str
    store_config: bool

    hibernate: bool
    verbosity: int


def _parse_args(argv):
    """
    >>> _parse_args([])
    _Options(n=1, channel=None, hibernate=False, verbosity=30)

    >>> _parse_args(['-n', '2'])
    _Options(n=2, channel=None, hibernate=False, verbosity=30)

    >>> _parse_args(['--channel', 'xyz'])
    _Options(n=1, channel='xyz', hibernate=False, verbosity=30)

    >>> _parse_args(["--hibernate"])
    _Options(n=1, channel=None, hibernate=True, verbosity=30)

    >>> _parse_args(["-v"])
    _Options(n=1, channel=None, hibernate=False, verbosity=20)

    >>> _parse_args(["-v", "-v"])
    _Options(n=1, channel=None, hibernate=False, verbosity=10)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", type=int, default=1, help="The number of new videos to watch for"
    )
    parser.add_argument(
        "--channel",
        type=str,
        help="(Optional) The channel id to monitor (default: load from config.yaml)",
    )
    parser.add_argument(
        "--store-config",
        action="store_true",
        help="Store channel in config and exit",
    )

    actions_group = parser.add_argument_group("Actions")
    actions_group.add_argument(
        "--hibernate",
        action="store_true",
        help="Hibernate computer once condition is met",
    )

    debug_group = parser.add_argument_group("debug")
    debug_group.add_argument(
        "--verbose",
        "-v",
        help="increase verbosity (may be repeated)",
        action="count",
        default=0,
    )
    debug_group.add_argument(
        "--quiet",
        "-q",
        help="decrease verbosity (may be repeated)",
        action="count",
        default=0,
    )

    parsed = parser.parse_args(argv)

    _verbosity = 2 + parsed.verbose - parsed.quiet
    _verbosity = max(0, _verbosity)
    _verbosity = min(4, _verbosity)
    parsed.verbosity = {
        0: logging.ERROR,
        1: logging.CRITICAL,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }[_verbosity]

    result = _Options(
        **{k: v for k, v in parsed.__dict__.items() if k in _Options._fields}
    )
    return result


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    options = _parse_args(argv)
    _main(options)


def _load_config():
    if not CONFIG_FILE.is_file():
        _MODULE_LOGGER.debug("no config file")
        return {}
    raw = CONFIG_FILE.read_text()
    parsed = yaml.safe_load(raw)
    _MODULE_LOGGER.debug("config loaded from %s", CONFIG_FILE)
    return parsed


def _get_channel_data(channel_id):
    URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    logging.info("Loading url: %s", URL)
    response = requests.get(URL)
    response.raise_for_status()
    response.raw.decode_content = True
    data = xmltodict.parse(response.content)
    return data


def _get_video_ids(content: dict):
    return [vid["id"] for vid in content.get("feed", {}).get("entry", [])]


def _get_video_ids_for_channel(channel):
    data = _get_channel_data(channel)
    return set(_get_video_ids(data))


def _setup_default_config():
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if CONFIG_FILE.is_file():
        _MODULE_LOGGER.info("Config file already exists, skipping")
        return

    CONFIG_FILE.write_text(
        textwrap.dedent(
            """\
        ---
        check_delay: 600  # 10 min * 60 s/min 
        """
        )
    )


def _main(options: _Options):
    logging.basicConfig(
        format="%(asctime)s  (%(levelname)s)  %(filename)s.%(funcName)s:%(message)s",
        level=options.verbosity,
    )

    if not CONFIG_FILE.is_file():
        print(f"Setting up default configuration in {CONFIG_FILE}")
        _setup_default_config()

    config = _load_config()
    channel = options.channel or config.get("channel")
    delay_between_checks = config.get("check_delay", 60 * 10)  # 60 s/min * 10 min

    if options.store_config:
        config = {
            "channel": channel,
            "check_delay": delay_between_checks,
        }
        _MODULE_LOGGER.debug("Writing config to file (%s):\n%s", CONFIG_FILE, config)
        with CONFIG_FILE.open("w") as config_fout:
            print("---", file=config_fout)
            yaml.safe_dump(config, config_fout)
        _MODULE_LOGGER.debug("Exiting")
        return 0

    logging.info("Pulling info for channel: %s", channel)
    if not channel:
        raise Exception(
            "Error, must provide either the --channel flag or set it in config.yaml"
        )

    current_videos = _get_video_ids_for_channel(channel)
    original_videos = current_videos

    _MODULE_LOGGER.warning(
        "Waiting for %s new video%s", options.n, "s" if options.n > 1 else ""
    )

    while True:
        new_videos = current_videos - original_videos
        _MODULE_LOGGER.warning(
            "Found %s new video%s", len(new_videos), "s" if len(new_videos) != 1 else ""
        )
        if len(new_videos) >= options.n:
            break

        time.sleep(delay_between_checks)  # don't need to constantly ping
        current_videos = _get_video_ids_for_channel(channel)

    if options.hibernate:
        os.system("shutdown /h")  # assumes windows

    _MODULE_LOGGER.warning("Exiting")


if __name__ == "__main__":
    main()
