#!/usr/bin/env python
import requests


class MonitorSite:
    """Class for monitoring the status of a website and checking it against an
     expected status.
    """
    def __init__(self, url, expected_status_code=200):
        self.status_code = None
        self.url = url
        self.expected_status_code = expected_status_code

    def get_status_code(self):
        if self.status_code:
            return self.status_code
        else:
            self.status_code = requests.get(url=self.url).status_code

    def check_status_code(self):
        if not self.status_code:
            self.get_status_code()

        if self.expected_status_code == self.status_code:
            return True
        else:
            return False

    def create_slack_message(self):
        message = ("Error at {url}. Expected status code expected: {expected}"
                   " | Actual status code: {actual}"
                   .format(url=self.url,
                           expected=self.expected_status_code,
                           actual=self.status_code)
                   )

        return message


def main():
    monitor_site = MonitorSite()

    print('URL: {}'.format(monitor_site.url))
    print('Expected Status Code: {}'.format(monitor_site.expected_status_code))
    print('Status Code: {}'.format(monitor_site.status_code))
    print('Status Code Matches Expected: {}'.format(monitor_site.check_status_code()))

if __name__ == '__main__':
    main()
