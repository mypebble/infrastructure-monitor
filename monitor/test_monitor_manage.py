import unittest
import yaml

from yaml.composer import ComposerError
from yaml.scanner import ScannerError

from mock import patch

from monitor.monitor_manager import MonitorManager, MalformedConfig,\
                                    NoConfigFound

from monitor.monitor_site import MonitorSite


class TestParseConfig(unittest.TestCase):
    yaml_config = ("---\n"
                   "sites:\n"
                   "- url: example.uk\n"
                   "  status_code: 200\n"
                   "- url: example.co.uk\n"
                   "  status_code: 302\n"
                   "domains:\n"
                   "- url: 8.8.8.8\n")

    yaml_config2 = ("---\n"
                    "domains:\n"
                    "- url: 8.8.8.8\n"
                    "sites:\n"
                    "- url: example.fr\n"
                    "  status_code: 200\n"
                    "- url: example.com\n"
                    "  status_code: 302\n")

    yaml_config3 = ("---\n"
                    "domains:\n"
                    "- url: 8.8.8.8\n")

    yaml_config4 = ("---\n"
                    "sites:\n"
                    "- url: example.fr\n"
                    "  status_code: 200\n"
                    "- url: example.com\n"
                    "  status_code: 302\n")

    yaml_config_single_site = ("---\n"
                               "sites:\n"
                               "- url: example.com\n"
                               "  status_code: 200")

    yaml_config_malformed = ("---"
                             "sites:"
                             "- url: example.com"
                             "  status_code: 200")

    yaml_config_malformed2 = ("aaaaaa\n"
                              "--- bbbbb")

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_sites_from_config(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config)
        manager = MonitorManager()
        manager.parse_config()

        sites = manager.sites

        for site in sites:
            self.assertTrue(isinstance(site, MonitorSite))

        self.assertEqual('example.uk', sites[0].url)
        self.assertEqual(200, sites[0].expected_status_code)

        self.assertEqual('example.co.uk', sites[1].url)
        self.assertEqual(302, sites[1].expected_status_code)

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_sites_from_config_reverse_input(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config2
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config2)
        manager = MonitorManager()
        manager.parse_config()

        sites = manager.sites

        for site in sites:
            self.assertTrue(isinstance(site, MonitorSite))

        self.assertEqual('example.fr', sites[0].url)
        self.assertEqual(200, sites[0].expected_status_code)

        self.assertEqual('example.com', sites[1].url)
        self.assertEqual(302, sites[1].expected_status_code)

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_sites_from_config_with_only_domains(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config3)
        manager = MonitorManager()
        manager.parse_config()

        sites = manager.sites

        self.assertEqual([], sites)

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_domains_from_config(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config)
        manager = MonitorManager()
        manager.parse_config()

        domains = manager.domains

        for domain in domains:
            self.assertTrue(isinstance(domain, str))

        self.assertEqual(domains[0], '8.8.8.8')

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_domains_from_config_reverse_input(self, mock_get_yaml_config):
        # Using yaml_config2
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config2)
        manager = MonitorManager()
        manager.parse_config()

        domains = manager.domains

        for domain in domains:
            self.assertTrue(isinstance(domain, str))

        self.assertEqual('8.8.8.8', domains[0])

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_domains_from_config_with_only_sites(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config4)
        manager = MonitorManager()
        manager.parse_config()

        domains = manager.domains

        self.assertEqual([], domains)

    @patch('yaml.load')
    def test_read_from_blank_config(self, mock_load):
        """Attempts to read from an empty config file
        """
        try:
            yaml.load("")
        except IOError as e:
            mock_load.side_effect = e

        manager = MonitorManager()

        self.assertEqual([], manager.sites)
        self.assertEqual([], manager.domains)

        self.assertRaises(NoConfigFound, manager.set_config())

        self.assertEqual([], manager.sites)
        self.assertEqual([], manager.domains)

    @patch('yaml.load')
    def test_malformed_config_file_composer_error(self, mock_load):
        """Attempts to read from a malformed config file
        """
        try:
            yaml.load(self.yaml_config_malformed)
        except ComposerError:
            mock_load.side_effect = ComposerError

        manager = MonitorManager()

        self.assertRaises(MalformedConfig, manager.parse_config())

    @patch('yaml.load')
    def test_malformed_config_file_scanner_error(self, mock_load):
        """Attempts to read from a malformed config file
        """
        try:
            yaml.load(self.yaml_config_malformed)
        except ScannerError:
            mock_load.side_effect = ComposerError

        manager = MonitorManager()

        self.assertRaises(MalformedConfig, manager.parse_config())

    @patch('slack.slack.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.requests')
    def test_status_code_expected(self, mock_requests, mock_get_yaml_config,
                                  mock_slack_post_message):
        """Test monitor manager doesn't send a message if the response status
        code matches the expected status code.
        """
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config_single_site)
        manager = MonitorManager()
        manager.parse_config()
        response_status_code = manager.sites[0].expected_status_code
        mock_requests.get.return_value.status_code = response_status_code
        manager.check_sites()

        mock_slack_post_message.assert_not_called()

    @patch('slack.slack.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.requests')
    def test_status_code_unexpected(self, mock_requests, mock_get_yaml_config,
                                    mock_slack_post_message):
        """Test monitor manager sends a message if the response status
        code does not match the expected status code.
        """
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config_single_site)
        manager = MonitorManager()
        manager.parse_config()
        response_status_code = manager.sites[0].expected_status_code + 1
        mock_requests.get.return_value.status_code = response_status_code
        manager.check_sites()

        mock_slack_post_message.assert_called_once()


if __name__ == '__main__':
    unittest.main()
