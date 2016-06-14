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
            data = load(yaml_file)
    except IOError:
        raise NoConfigFound
    except (ComposerError, ScannerError):
        raise MalformedConfig

    return data


class MalformedConfig(Exception):
    def __init__(self):
        super(MalformedConfig, self).__init__(
            "A malformed config file has been found. Please check the "
            "formatting of your config.yaml file.")


class NoConfigFound(Exception):
    def __init__(self):
        super(NoConfigFound, self).__init__(
            "No config file has been found. Please ensure you have a "
            "config.yaml file and it is correctly formatted.")


class MonitorManager:
    def __init__(self):
        self.sites = []
        self.domains = []
        self.config = None
        self.slack = Slack()

    def set_config(self, config_file="config.yaml"):
        try:
            self.config = get_yaml_config(config_file)
        except (NoConfigFound, MalformedConfig) as e:
            self.slack.post_message(e.message)

    def parse_config(self):
        if not self.config:
            self.set_config()

        if self.config:
            for site in self.config.get('sites', []):
                _site = MonitorSite(site['url'], site['status_code'])
                self.sites.append(_site)

            for domain in self.config.get('domains', []):
                self.domains.append(domain['url'])

    def check_sites(self):
        errors = [site.create_slack_message() for site in self.sites
                  if not site.check_status_code()]

        for error in errors:
            self.slack.post_message(error)

        return len(errors)


def main():
    manager = MonitorManager()
    manager.parse_config()
    print(manager.sites)
    manager.check_sites()

if __name__ == '__main__':
    main()
