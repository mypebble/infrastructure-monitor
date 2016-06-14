import unittest
import yaml

from yaml.composer import ComposerError
from yaml.scanner import ScannerError

from requests.exceptions import MissingSchema

from mock import patch

from monitor.monitor_manager import (MonitorManager, MalformedConfig,
                                     NoConfigFound, get_yaml_config)

from monitor.monitor_site import MonitorSite


class TestParseConfig(unittest.TestCase):
    yaml_config = (
        "---\n"
        "sites:\n"
        "- url: example.uk\n"
        "  status_code: 200\n"
        "- url: example.co.uk\n"
        "  status_code: 302\n"
        "domains:\n"
        "- url: 8.8.8.8\n")

    yaml_config2 = (
        "---\n"
        "domains:\n"
        "- url: 8.8.8.8\n"
        "sites:\n"
        "- url: example.fr\n"
        "  status_code: 200\n"
        "- url: example.com\n"
        "  status_code: 302\n")

    yaml_config3 = (
        "---\n"
        "domains:\n"
        "- url: 8.8.8.8\n")

    yaml_config4 = (
        "---\n"
        "sites:\n"
        "- url: example.fr\n"
        "  status_code: 200\n"
        "- url: example.com\n"
        "  status_code: 302\n")

    yaml_config5 = (
        "---\n"
        "sites:\n"
        "- url: example.fr\n"
        "  status_code: 200\n"
        "- url: example.com\n"
        "  status_code: 302\n"
        "- url: example.org\n"
        "  status_code: 200\n"
        "- url: example.co.uk\n"
        "  status_code: 302\n")

    yaml_config_single_site = (
        "---\n"
        "sites:\n"
        "- url: example.com\n"
        "  status_code: 200\n")

    yaml_config_multiple_sites = (
        "---\n"
        "sites:\n"
        "- url: example.com\n"
        "  status_code: 200\n"
        "- url: example.org\n"
        "  status_code: 200\n")

    yaml_config_malformed = (
        "aaaaaa\n"
        "--- bbbbb\n")

    yaml_config_malformed2 = (
        "---"
        "sites:"
        "- url: example.com"
        "  status_code: 200\n")

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_sites_config(self, mock_get_yaml_config):
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
    def test_read_sites_config_reverse_input(self, mock_get_yaml_config):
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
    def test_read_sites_config_with_only_domains(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config3)
        manager = MonitorManager()
        manager.parse_config()

        sites = manager.sites

        self.assertEqual([], sites)

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_site.get')
    @patch('monitor.monitor_manager.get_yaml_config')
    def test_site_without_protocol(self, mock_get_yaml_config, mock_requests,
                                   mock_slack):
        # Part 1 with yaml_config4
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config4)
        mock_requests.side_effects = MissingSchema
        manager = MonitorManager()
        manager.parse_config()
        manager.check_sites()

        mock_slack.assert_called_once()

        # Called twice because yaml_config4 has two sites in it
        self.assertEqual(2, mock_slack.call_count)

        # Part 2 with yaml_config5
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config5)
        mock_requests.side_effects = MissingSchema
        manager = MonitorManager()
        manager.parse_config()
        manager.check_sites()

        # Called four times because yaml_config5 has four sites in it
        self.assertEqual(4, mock_slack.call_count)

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_domains_config(self, mock_get_yaml_config):
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
    def test_read_domains_config_reverse_input(self, mock_get_yaml_config):
        # Using yaml_config2
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config2)
        manager = MonitorManager()
        manager.parse_config()

        domains = manager.domains

        for domain in domains:
            self.assertTrue(isinstance(domain, str))

        self.assertEqual('8.8.8.8', domains[0])

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_domains_config_with_only_sites(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config4)
        manager = MonitorManager()
        manager.parse_config()

        domains = manager.domains

        self.assertEqual([], domains)

    def test_read_blank_config(self):
        """Attempts to read from an empty config file
        """
        self.assertRaises(NoConfigFound, get_yaml_config, "")

    @patch('monitor.monitor_manager.open')
    def test_malformed_config_file_raises_composer_error(self, mock_open):
        """Attempts to read from a malformed config file
        """
        mock_open.return_value.__enter__.return_value = \
            self.yaml_config_malformed

        self.assertRaises(ComposerError, yaml.load, self.yaml_config_malformed)

        self.assertRaises(MalformedConfig, get_yaml_config)

    @patch('monitor.monitor_manager.open')
    def test_malformed_config_file_raises_scanner_error(self, mock_open):
        """Attempts to read from a malformed config file
        """
        mock_open.return_value.__enter__.return_value = \
            self.yaml_config_malformed2

        self.assertRaises(ScannerError, yaml.load, self.yaml_config_malformed2)

        self.assertRaises(MalformedConfig, get_yaml_config)

    @patch('slack.slack.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_code_expected_single(self, mock_requests,
            mock_get_yaml_config, mock_slack_post_message):
        """Test monitor manager doesn't send a message if the response status
        code matches the expected status code.
        """
        mock_get_yaml_config.return_value = yaml.load(
            self.yaml_config_single_site)
        manager = MonitorManager()
        manager.parse_config()
        response_status_code = manager.sites[0].expected_status_code
        mock_requests.return_value.status_code = response_status_code
        manager.check_sites()

        mock_slack_post_message.assert_not_called()

    @patch('slack.slack.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_code_unexpected_single(self, mock_requests,
            mock_get_yaml_config, mock_slack_post_message):
        """Test monitor manager sends a message if the response status
        code does not match the expected status code.
        """
        mock_get_yaml_config.return_value = yaml.load(
            self.yaml_config_single_site)
        manager = MonitorManager()
        manager.parse_config()
        response_status_code = manager.sites[0].expected_status_code + 1
        mock_requests.return_value.status_code = response_status_code
        manager.check_sites()

        mock_slack_post_message.assert_called_once()

    @patch('slack.slack.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_codes_expected_multiple(self,
                                            mock_requests,
                                            mock_get_yaml_config,
                                            mock_slack_post_message):
        """Test monitor manager doesn't send a message if the response status
        code matches the expected status code.
        """
        mock_get_yaml_config.return_value = yaml.load(
            self.yaml_config_multiple_sites)
        manager = MonitorManager()
        manager.parse_config()
        response_status_code = manager.sites[0].expected_status_code
        mock_requests.return_value.status_code = response_status_code
        response_status_code = manager.sites[1].expected_status_code
        mock_requests.return_value.status_code = response_status_code

        manager.check_sites()

        mock_slack_post_message.assert_not_called()

    @patch('slack.slack.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_codes_unexpected_multiple(self,
                                              mock_requests,
                                              mock_get_yaml_config,
                                              mock_slack_post_message):
        """Test monitor manager sends a message if the response status
        code does not match the expected status code.
        """
        mock_get_yaml_config.return_value = yaml.load(
            self.yaml_config_multiple_sites)
        manager = MonitorManager()
        manager.parse_config()
        response_status_code = manager.sites[0].expected_status_code + 1
        mock_requests.get.return_value.status_code = response_status_code
        manager.check_sites()

        self.assertEqual(2, mock_slack_post_message.call_count)


if __name__ == '__main__':
    unittest.main()
