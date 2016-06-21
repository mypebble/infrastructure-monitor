#!/usr/bin/env python
"""Used to manage the config and monitoring of sites and domains.

Sends a message to Slack if there are any issues detected.
"""
import sys
import getopt
import logging

from raven import Client
from monitor.monitor_manager import MonitorManager

from monitor.parse_yaml import get_yaml_config


logging.basicConfig(filename='infrastructure-monitor.log',
                    level=logging.INFO,
                    format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - '
                           '%(funcName)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")


def main(argv=None):
    logging.info("Started program.")

    try:
        opts, args = getopt.getopt(argv, "hc:s:e:",
                                   ["configfile=", "slack-configfile=",
                                    "error-sentry-configfile="])
    except getopt.GetoptError as e:
        print('main.py -c <configfile> -s <slack-configfile> '
              '-e <error-sentry_configfile')

        logging.error(u"Invalid parameters passed in: ".format(
            error=unicode(e.message)))
        sys.exit(2)

    try:
        config = "config.yaml"
        slack_config = "slack_config.yaml"
        sentry_config = "sentry_config.yaml"

        for opt, arg in opts:
            if opt == '-h':
                print('main.py -c <configfile> -s <slack-configfile> '
                      '-e <error-sentry_configfile')
                sys.exit()
            elif opt in ("-c", "--config"):
                config = arg
            elif opt in ("-s", "--slack-configfile"):
                slack_config = arg
            elif opt in ("-e", "--error-sentry-configfile"):
                sentry_config = arg

        sentry_config_data = get_yaml_config(sentry_config)

        if sentry_config_data['sentry_dsn'] is not None:
            client = Client(sentry_config_data['sentry_dsn'])

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

        logging.debug("Parsing config.")
        manager.parse_config()
        logging.debug("Config parsed.")

        logging.debug("Checking sites.")
        manager.check_sites()
        logging.debug("Sites checked.")

        logging.debug("Checking domains.")
        manager.check_domains()
        logging.debug("Domains checked.")

        logging.info("Finished program.")
    except KeyboardInterrupt as e:
        sys.exit(e.message)
    except Exception as e:
        logging.error(u"Exiting from an error: {error}".format(
            error=unicode(e.message)))

        if config is not None:
            client.captureException()

        sys.exit(e.message)

if __name__ == '__main__':
    main(sys.argv[1:])
