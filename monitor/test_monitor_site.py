import unittest

from mock import patch

from monitor.monitor_site import MonitorSite


class TestMonitor(unittest.TestCase):

    @patch('monitor.monitor_site.requests')
    def test_get_200_ok_status_code(self, mock_requests):
        """This checks that the function returns the 200 status code
         when a GET request to a valid url is sent
        """
        mock_requests.get.return_value.status_code = 200

        url = "http://example.com"
        expected_status_code = 200
        monitor = MonitorSite(url=url, expected_status_code=expected_status_code)
        monitor.get_status_code()

        self.assertEqual(url, monitor.url)
        self.assertEqual(expected_status_code, monitor.expected_status_code)
        self.assertEqual(expected_status_code, monitor.status_code)


    @patch('monitor.monitor_site.requests')
    def test_check_status_code_matches_expected(self, mock_requests):
        """Checks that the status code from the GET request matches the
        expected status code
        """
        mock_requests.get.return_value.status_code = 200

        url = "http://example.com"
        expected_status_code = 200
        monitor = MonitorSite(url=url, expected_status_code=expected_status_code)
        monitor.get_status_code()

        status_code = monitor.status_code
        self.assertEqual(expected_status_code, status_code)

        output = monitor.check_status_code()
        self.assertEqual(True, output)

    @patch('monitor.monitor_site.requests')
    def test_check_status_code_does_not_match_expected(self, mock_requests):
        mock_requests.get.return_value.status_code = 503

        url = "http://example.com"
        expected_status_code = 200
        monitor = MonitorSite(url=url, expected_status_code=expected_status_code)
        monitor.get_status_code()

        status_code = monitor.status_code
        self.assertNotEqual(expected_status_code, status_code)

        output = monitor.check_status_code()
        self.assertEqual(False, output)

    @patch('monitor.monitor_site.requests')
    def test_check_status_gets_status_if_not_called(self, mock_requests):
        mock_requests.get.return_value.status_code = 404

        url = "http://example.com"
        expected_status_code = 404
        monitor = MonitorSite(url=url, expected_status_code=expected_status_code)

        status_code = monitor.status_code
        self.assertEqual(None, status_code)

        output = monitor.check_status_code()
        self.assertEqual(True, output)

        status_code = monitor.status_code
        self.assertEqual(expected_status_code, status_code)

    def test_protocol_is_added_if_missing(self):
        url_missing_protocol = "example.com"
        url_with_protocol = "http://example.com"
        expected_status_code = 200

        monitor = MonitorSite(url=url_missing_protocol,
                              expected_status_code=expected_status_code)

        self.assertEqual(url_with_protocol, monitor.url)

    def test_protocol_is_not_added_if_there(self):
        url_missing_protocol = "http://example.com"
        url_with_protocol = "http://example.com"
        expected_status_code = 200

        monitor = MonitorSite(url=url_missing_protocol,
                              expected_status_code=expected_status_code)

        self.assertEqual(url_with_protocol, monitor.url)

        url_missing_protocol = "https://example.com"
        url_with_protocol = "https://example.com"
        expected_status_code = 200

        monitor = MonitorSite(url=url_missing_protocol,
                              expected_status_code=expected_status_code)

        self.assertEqual(url_with_protocol, monitor.url)
