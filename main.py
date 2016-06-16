#!/usr/bin/env python
"""Used to manage the config and monitoring of sites and domains.

Sends a message to Slack if there are any issues detected.
"""
import sys
import getopt

from monitor.monitor_manager import MonitorManager


def main(argv=None):
    try:
        opts, args = getopt.getopt(argv, "hc:s:", ["config=", "slackconfig="])
    except getopt.GetoptError:
        print('main.py -c <configfile> -s <slack-configfile>')
        sys.exit(2)

    config = None
    slack_config = None

    for opt, arg in opts:
        if opt == '-h':
            print('main.py -c <configfile> -s <slack-configfile>')
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
        print(u"Exiting from an error:\n{error}".format(
            error=unicode(e.message)))
        sys.exit(e.message)

if __name__ == '__main__':
    main(sys.argv[1:])
