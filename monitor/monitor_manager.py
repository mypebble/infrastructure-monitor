#!/usr/bin/env python
"""Used to manage the config and monitoring of sites and domains.

Sends a message to Slack if there are any issues detected.
"""

import yaml


class MonitorManager:
    sites = []

    def __init__(self):
        self.parse_config()

    def parse_config(self):
        config = self.get_yaml_config()

        if config:
            for site in config['sites']:
                _site = Site(url=site['url'], expected_status_code=site['status_code'])

                self.sites.append(_site)

    @staticmethod
    def get_yaml_config():
        config_file = "config.yaml"
        try:
            with open(config_file, 'r') as yamlfile:
                return yaml.load(yamlfile)
        except:
            return None


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
