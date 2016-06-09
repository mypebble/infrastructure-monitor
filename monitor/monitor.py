#!/usr/bin/env python
"""Used to monitor the status of a website.
"""

import requests


class MonitorSite:

    def __init__(self, url="http://example.com", expected_status_code=200):
        self.url = url
        self.expected_status_code = expected_status_code
        self.status_code = self.get_status_code()

    def check_status_code(self):
        if self.expected_status_code == self.status_code:
            return True
        else:
            return False

    def get_status_code(self):
        return requests.get(url=self.url).status_code
