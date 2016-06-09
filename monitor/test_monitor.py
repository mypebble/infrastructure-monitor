import unittest

from monitor import get_status_code


class TestMonitor(unittest.TestCase):

    def test_get_200_ok_status_code(self):
        """This checks that the function returns the 200 status code
         when a GET request to a valid url is sent
        """
        url = "200ok.com"
        status_code = get_status_code(url)

        self.assertEqual(status_code, 200)
