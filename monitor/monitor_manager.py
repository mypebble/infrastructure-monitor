#!/usr/bin/env python
"""Used to manage the config and monitoring of sites and domains.

Sends a message to Slack if there are any issues detected.
"""

import yaml


def get_yaml_config():
    config_file = "config.yaml"
    try:
        with open(config_file, 'r') as yaml_file:
            return yaml.load(yaml_file)
    except IOError:
        return None


class MonitorManager:
    def __init__(self):
        self.sites = []
        self.parse_config()

    def parse_config(self):
        config = get_yaml_config()
        if config:
            for site in config['sites']:
                _site = Site(url=site['url'], expected_status_code=site['status_code'])
                self.sites.append(_site)


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
