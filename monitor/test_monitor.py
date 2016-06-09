import unittest

from mock import patch

from monitor import Monitor


class TestMonitor(unittest.TestCase):

    @patch('monitor.requests')
    def test_get_200_ok_status_code(self, mock_requests):
        """This checks that the function returns the 200 status code
         when a GET request to a valid url is sent
        """
        mock_requests.get.return_value.status_code = 200

        url = "http://example.com"
        expected_status_code = 200
        monitor = Monitor(url=url, expected_status_code=expected_status_code)

        status_code = monitor.get_status_code()

        self.assertEqual(status_code, expected_status_code)
