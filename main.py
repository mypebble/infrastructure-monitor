#!/usr/bin/env python
"""Used to manage the config and monitoring of sites and domains.

Sends a message to Slack if there are any issues detected.
"""
import sys

from monitor.monitor_manager import MonitorManager
from slack.slack import Slack


def main():
    try:
        manager = MonitorManager()
        manager.parse_config()
        manager.check_sites()
    except KeyboardInterrupt as e:
        sys.exit(e.message)
    except Exception as e:
        slack = Slack()
        slack.post_message(e.message)
        sys.exit(e.message)

if __name__ == '__main__':
    main()
