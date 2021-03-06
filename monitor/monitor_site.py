#!/usr/bin/env python
from requests import get
from requests.exceptions import ReadTimeout


class MonitorSite(object):
    """Class for monitoring the status of a website and checking it against an
     expected status.
    """
    def __init__(self, url, expected_status_code=200, slack=None):
        self.status_code_history = None
        self.status_code = None
        self.url = url
        self.slack = slack

        if expected_status_code is not None:
            self.expected_status_code = expected_status_code
        else:
            self.expected_status_code = 200

    def __unicode__(self):
            return u"(URL: {url}, Expected Status Code: {status_code})".format(
                url=self.url,
                status_code=self.expected_status_code)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def get_status_code(self):
        if self.status_code is None:

            try:
                response = get(url=self.url, timeout=10.0)
            except ReadTimeout as e:
                error = self.create_slack_message(e.message)
                self.slack.post_message(error)
                return None

            self.status_code = response.status_code

            self._expected_redirect(response)

        return self.status_code

    def _expected_redirect(self, response):
        if str(self.expected_status_code).startswith('3'):
            try:
                self.status_code_history = response.history[0].status_code
            except IndexError:
                self.status_code_history = None

    def check_status_code(self):
        if not self.status_code:
            self.get_status_code()

        if (self.expected_status_code == self.status_code_history and
                200 == self.status_code):
            return True
        elif self.expected_status_code == self.status_code:
            return True
        else:
            return False

    def create_slack_message(self, error=None):
        if error is None:
            message = ("Error at {url}. Expected status code expected: "
                       "{expected} | Actual status code: {actual}"
                       .format(url=self.url,
                               expected=self.expected_status_code,
                               actual=self.status_code)
                       )
        else:
            message = ("Error at {url}. {error}".format(url=self.url,
                                                        error=error))

        return message


def main():
    monitor_site = MonitorSite("http://example.com")

    print('URL: {}'.format(monitor_site.url))
    print('Expected Status Code: {}'.format(monitor_site.expected_status_code))
    print('Status Code: {}'.format(monitor_site.get_status_code()))
    print('Status Code Matches Expected: {}'.format(monitor_site.check_status_code()))

if __name__ == '__main__':
    main()
