#!/usr/bin/env python
"""Used to monitor the status of a website.
"""

import requests


class MonitorSite:
    url = None
    expected_status_code = None
    status_code = None

    def __init__(self, url="http://example.com", expected_status_code=200):
        self.url = url
        self.expected_status_code = expected_status_code
        self.status_code = self.get_status_code()

    def get_status_code(self):
        if self.status_code:
            return self.status_code
        else:
            return requests.get(url=self.url).status_code

    def check_status_code(self):
        if self.expected_status_code == self.status_code:
            return True
        else:
            return False


def main():
    monitor_site = MonitorSite()

    print('URL: {}'.format(monitor_site.url))
    print('Expected Status Code: {}'.format(monitor_site.expected_status_code))
    print('Status Code: {}'.format(monitor_site.status_code))
    print('Status Code Matches Expected: {}'.format(monitor_site.check_status_code()))

if __name__ == '__main__':
    main()
