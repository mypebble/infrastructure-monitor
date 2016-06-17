#!/usr/bin/env python
"""Used to manage the config and monitoring of sites and domains.

Sends a message to Slack if there are any issues detected.
"""
from requests.exceptions import ConnectionError, MissingSchema, Timeout
from dns.resolver import NXDOMAIN
from dns.exception import DNSException, SyntaxError, Timeout, FormError, TooBig

from slack.slack import Slack

from monitor.parse_yaml import get_yaml_config, NoConfigFound, MalformedConfig

from monitor_site import MonitorSite
from monitor_domain import MonitorDomain


class MonitorManager(object):
    def __init__(self, config_file="config.yaml",
                 slack_config_file="slack_config.yaml"):
        self.config_file = config_file
        self.slack_config_file = slack_config_file
        self.parsed_config = None
        self.parsed_slack_config = None
        self.sites = []
        self.domains = []

        self.set_config()

        self.slack = Slack(self.parsed_slack_config)

    def set_config(self):
        try:
            self.parsed_config = get_yaml_config(self.config_file)
            self.parsed_slack_config = get_yaml_config(self.slack_config_file)
        except (NoConfigFound, MalformedConfig) as e:
            self.slack.post_message(e.message)

    def parse_config(self):
        self.sites = []
        self.domains = []

        if self.parsed_config:
            for site in self.parsed_config.get('sites', []):
                self.parse_site(site)

            for domain in self.parsed_config.get('domains', []):
                self.parse_domain(domain)

    def parse_site(self, site):
        try:
            if site['url']:
                _site = MonitorSite(site['url'], site.get(
                    'status_code', 200))
                self.sites.append(_site)
            else:
                raise KeyError
        except KeyError:
            self.slack.post_message("KeyError: Check the url field in your "
                                    "config.utils, it appears to be missing!")

    def parse_domain(self, domain):
        try:
            if domain['domain']:
                _domain = MonitorDomain(domain.get('domain'))
                self.domains.append(_domain)
        except KeyError:
            self.slack.post_message("KeyError: Check the domain field in your "
                                    "config.utils, it appears to be missing!")

    def check_sites(self):
        errors = []

        try:
            errors = [site.create_slack_message() for site in self.sites
                      if not site.check_status_code()]
        except (ConnectionError, MissingSchema, Timeout) as e:
            self.slack.post_message(unicode(e.message))

        for error in errors:
            self.slack.post_message(error)

        return len(errors)

    def check_domains(self):
        errors = []

        try:
            errors = [domain.create_slack_message() for domain in self.domains
                      if not domain.check_domain()]
        except (NXDOMAIN. DNSException, SyntaxError, Timeout, FormError,
                TooBig) as e:
            self.slack.post_message(unicode(e.message))

        for error in errors:
            self.slack.post_message(error)

        return len(errors)


def main():
    manager = MonitorManager(config_file="../config.yaml",
                             slack_config_file="../slack_config.yaml")
    manager.parse_config()
    print(manager.sites)
    manager.check_sites()

if __name__ == '__main__':
    main()
