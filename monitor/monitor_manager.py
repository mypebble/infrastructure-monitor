#!/usr/bin/env python
"""Used to manage the config and monitoring of sites and domains.

Sends a message to Slack if there are any issues detected.
"""
from yaml import load
from yaml.composer import ComposerError
from yaml.scanner import ScannerError

from monitor_site import MonitorSite
from slack.slack import Slack


def get_yaml_config(config_file="config.yaml"):
    try:
        with open(config_file, 'r') as yaml_file:
            return load(yaml_file)
    except IOError:
        raise NoConfigFound
    except ComposerError:
        raise MalformedConfig
    except ScannerError:
        raise MalformedConfig


class MalformedConfig(Exception):
    def __init__(self):
        Exception.__init__(self, "A malformed config file has been found. "
                                 "Check the formatting")


class NoConfigFound(Exception):
    def __init__(self):
        Exception.__init__(self, "No config file has been found")


class MonitorManager:
    def __init__(self):
        self.sites = []
        self.domains = []
        self.config = None

    def set_config(self, config_file="config.yaml"):
        self.config = get_yaml_config(config_file)

    def parse_config(self):
        if not self.config:
            self.set_config()

        if self.config:
            if 'sites' in self.config:
                for site in self.config['sites']:
                    _site = MonitorSite(url=site['url'],
                                        expected_status_code=site['status_code'])
                    self.sites.append(_site)

            if 'domains' in self.config:
                for domain in self.config['domains']:
                    self.domains.append(domain['url'])

    def check_sites(self):
        error_counter = 0

        if len(self.sites) > 0:
            slack = Slack()
            for site in self.sites:
                if not site.check_status_code():
                    slack.post_message(site.create_slack_message())
                    error_counter += 1

        return error_counter


class Site:
    def __init__(self, url, expected_status_code):
        self.url = url
        self.expected_status_code = expected_status_code

    def __str__(self):
        return "(URL: {url}, Expected Status Code: {status_code})"\
            .format(url=self.url,
                    status_code=self.expected_status_code)

    def __repr__(self):
        return self.__str__()


def main():
    monitor_manager = MonitorManager()
    print(monitor_manager.sites)

if __name__ == '__main__':
    main()
