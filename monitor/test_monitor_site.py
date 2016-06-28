import unittest

from mock import patch
from requests.exceptions import MissingSchema, ReadTimeout

from monitor.monitor_site import MonitorSite
from slack.slack import Slack


class TestMonitorSite(unittest.TestCase):
    slack_config = {
        'slack_api_token': '',
        'slack_channel': '',
        'slack_emote': '',
        'slack_shoutout': '',
        'slack_username': ''}

    @patch('monitor.monitor_site.get')
    def test_get_200_ok_status_code(self, mock_requests):
        """This checks that the function returns the 200 status code
         when a GET request to a valid url is sent
        """
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.history = []
        mock_requests.history[0].status_code.side_effect = IndexError

        url = "http://example.com"
        expected_status_code = 200
        monitor = MonitorSite(url=url,
                              expected_status_code=expected_status_code)

        try:
            monitor.get_status_code()
        except Exception as e:
            print(e.message)
            self.fail(e.message)

        self.assertEqual(url, monitor.url)
        self.assertEqual(expected_status_code, monitor.expected_status_code)
        self.assertEqual(expected_status_code, monitor.status_code)

    @patch('monitor.monitor_site.get')
    def test_check_status_code_matches_expected(self, mock_requests):
        """Checks that the status code from the GET request matches the
        expected status code
        """
        mock_requests.return_value.status_code = 200

        url = "http://example.com"
        expected_status_code = 200
        monitor = MonitorSite(url=url,
                              expected_status_code=expected_status_code)
        monitor.get_status_code()

        status_code = monitor.status_code
        self.assertEqual(expected_status_code, status_code)

        output = monitor.check_status_code()
        self.assertEqual(True, output)

    @patch('monitor.monitor_site.get')
    def test_check_status_code_does_not_match_expected(self, mock_requests):
        mock_requests.get.return_value.status_code = 503

        url = "http://example.com"
        expected_status_code = 200
        monitor = MonitorSite(url=url,
                              expected_status_code=expected_status_code)
        monitor.get_status_code()

        status_code = monitor.status_code
        self.assertNotEqual(expected_status_code, status_code)

        output = monitor.check_status_code()
        self.assertEqual(False, output)

    @patch('monitor.monitor_site.get')
    def test_check_status_gets_status_if_not_called(self, mock_requests):
        mock_requests.return_value.status_code = 404

        url = "http://example.com"
        expected_status_code = 404
        monitor = MonitorSite(url=url,
                              expected_status_code=expected_status_code)

        status_code = monitor.status_code
        self.assertEqual(None, status_code)

        output = monitor.check_status_code()
        self.assertEqual(True, output)

        status_code = monitor.status_code
        self.assertEqual(expected_status_code, status_code)

    def test_get_status_code_with_bad_url(self):
        # No prefix or suffixes
        bad_url = "url"
        expected_status_code = 200

        monitor = MonitorSite(url=bad_url,
                              expected_status_code=expected_status_code)

        self.assertRaises(MissingSchema, monitor.get_status_code)

        bad_url = "url.com"
        expected_status_code = 200

        monitor = MonitorSite(url=bad_url,
                              expected_status_code=expected_status_code)

        self.assertRaises(MissingSchema, monitor.get_status_code)

    @patch('monitor.monitor_site.get')
    def test_get_redirect(self, mock_requests):
        """This checks that the function returns the 200 status code
         when a GET request to a valid url is sent
        """
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.history[0].status_code = 302

        url = "http://example.com"
        expected_status_code = 302
        monitor = MonitorSite(url=url,
                              expected_status_code=expected_status_code)

        monitor.get_status_code()

        self.assertEqual(url, monitor.url)
        self.assertEqual(expected_status_code, monitor.expected_status_code)
        self.assertEqual(200, monitor.status_code)
        self.assertEqual(expected_status_code, monitor.status_code_history)

    @patch('slack.slack.Slack.post_message')
    @patch('monitor.monitor_site.get')
    def test_get_status_code_timeout(self, mock_requests,
                                     mock_slack_post_message):
        mock_requests.side_effect = ReadTimeout

        url = "http://example.com"
        expected_status_code = 200

        monitor = MonitorSite(url=url,
                              expected_status_code=expected_status_code,
                              slack=Slack(self.slack_config))

        monitor.get_status_code()
        self.assertEqual(1, mock_slack_post_message.call_count)

        status_code = monitor.status_code
        self.assertNotEqual(expected_status_code, status_code)

        output = monitor.check_status_code()
        self.assertEqual(False, output)

        self.assertEqual(2, mock_slack_post_message.call_count)
