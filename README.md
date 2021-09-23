# youtube_monitor_action
A utility to perform an action after videos are live on YouTube for a given channel.

This module provides the script `youtube-monitor-action`
```
usage: youtube-monitor-action [-h] [-n N] [--channel CHANNEL] [--store-config]
                              [--hibernate] [--open-in-browser] [--verbose]
                              [--quiet] [--version] [--log-file LOG_FILE]

optional arguments:
  -h, --help           show this help message and exit
  -n N                 The number of new videos to watch for
  --channel CHANNEL    (Optional) The channel id to monitor (default: load
                       from config.yaml)
  --store-config       Store channel and other settings in config and exit

Actions:
  --hibernate          Hibernate computer once condition is met
  --open-in-browser    Open new videos in browser

debug:
  --verbose, -v        increase verbosity (may be repeated)
  --quiet, -q          decrease verbosity (may be repeated)
  --version, -V        print version and exit

logging:
  --log-file LOG_FILE  File to log to
```
