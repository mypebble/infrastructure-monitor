#!/usr/bin/env python
"""Used to manage the config and monitoring of sites and domains.

Sends a message to Slack if there are any issues detected.
"""
import sys
import getopt
import logging

from monitor.monitor_manager import MonitorManager

from raven import Client


client = Client('https://7b44b294b11c4b5a88a69c22df64b480:6934c880b80f4e6aa14e'
                'b9513a3e65b6@app.getsentry.com/83436')

logging.basicConfig(filename='infrastructure-monitor.log', level=logging.INFO)


def main(argv=None):
    try:
        opts, args = getopt.getopt(argv, "hc:s:", ["config=", "slackconfig="])
    except getopt.GetoptError as e:
        print('main.py -c <configfile> -s <slack-configfile>')

        logging.error(u"Invalid parameters passed in: ".format(
            error=unicode(e.message)))
        client.captureException()
        sys.exit(2)

    try:
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
        logging.error(u"Exiting from an error:\n{error}".format(
            error=unicode(e.message)))
        client.captureException()
        sys.exit(e.message)

if __name__ == '__main__':
    main(sys.argv[1:])
