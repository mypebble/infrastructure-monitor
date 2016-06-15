#!/usr/bin/env python
"""Used to manage the config and monitoring of sites and domains.

Sends a message to Slack if there are any issues detected.
"""
import sys
import getopt

from monitor.monitor_manager import MonitorManager
from slack.slack import Slack


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hc:s:", ["config=", "slackconfig="])
    except getopt.GetoptError:
        print 'test.py -c <configfile> -s <slack-configfile>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -c <configfile> -s <slack-configfile>'
            sys.exit()
        elif opt in ("-c", "--config"):
            config = arg
        elif opt in ("-s", "--slack-configfile"):
            slack_config = arg

    try:
        # There must be a nicer way of doing this...
        if config and slack_config:
            manager = MonitorManager(config_file=config,
                                     slack_config_file=slack_config)
        elif config and not slack_config:
            manager = MonitorManager(config_file=config)
        elif not config and slack_config:
            manager = MonitorManager(slack_config_file=slack_config)
        else:
            manager = MonitorManager()

        manager.parse_config()
        manager.check_sites()
    except KeyboardInterrupt as e:
        sys.exit(e.message)
    except Exception as e:
        # TODO - Switch to logger.error and raise something to Sentry
        slack = Slack()
        slack.post_message(e.message)
        sys.exit(e.message)

if __name__ == '__main__':
    main(sys.argv[1:])
