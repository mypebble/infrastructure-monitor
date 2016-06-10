import unittest

from mock import patch

from monitor_site import MonitorSite


class TestMonitor(unittest.TestCase):

    @patch('monitor.requests')
    def test_get_200_ok_status_code(self, mock_requests):
        """This checks that the function returns the 200 status code
         when a GET request to a valid url is sent
        """
        mock_requests.get.return_value.status_code = 200

        url = "http://example.com"
        expected_status_code = 200
        monitor = MonitorSite(url=url, expected_status_code=expected_status_code)

        status_code = monitor.get_status_code()

        self.assertEqual(expected_status_code, status_code)

    @patch('monitor.requests')
    def test_check_status_code_matches(self, mock_requests):
        """Checks that the status code from the GET request matches the
        expected status code
        """
        mock_requests.get.return_value.status_code = 200

        url = "http://example.com"
        expected_status_code = 200
        monitor = MonitorSite(url=url, expected_status_code=expected_status_code)

        output = monitor.check_status_code()

        self.assertEqual(True, output)

    @patch('monitor.requests')
    def test_check_status_code_does_not_match(self, mock_requests):
        mock_requests.get.return_value.status_code = 503

        url = "http://example.com"
        expected_status_code = 200
        monitor = MonitorSite(url=url, expected_status_code=expected_status_code)

        output = monitor.check_status_code()

        self.assertEqual(False, output)
