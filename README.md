# youtube_monitor_action
A utility to perform an action after videos are live on YouTube for a given channel.

This module provides the script `wait-for-videos`
```
usage: wait-for-videos [-h] [-n N] [--channel CHANNEL] [--store-config] [--hibernate] [--verbose] [--quiet]
                       [--log-file LOG_FILE]

optional arguments:
  -h, --help           show this help message and exit
  -n N                 The number of new videos to watch for
  --channel CHANNEL    (Optional) The channel id to monitor (default: load from config.yaml)
  --store-config       Store channel and other settings in config and exit

Actions:
  --hibernate          Hibernate computer once condition is met

debug:
  --verbose, -v        increase verbosity (may be repeated)
  --quiet, -q          decrease verbosity (may be repeated)

logging:
  --log-file LOG_FILE  File to log to
```
