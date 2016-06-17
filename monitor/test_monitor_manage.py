import unittest
import yaml

from mock import patch
from monitor.monitor_manager import (MonitorManager, MalformedConfig,
                                     NoConfigFound)
from monitor.monitor_site import MonitorSite
from monitor.monitor_domain import MonitorDomain
from monitor.parse_yaml import get_yaml_config
from requests.exceptions import ConnectionError, MissingSchema
from yaml.composer import ComposerError
from yaml.parser import ParserError
from yaml.scanner import ScannerError


class TestMonitorManager(unittest.TestCase):
    slack_config = {
        'slack_api_token': '',
        'slack_channel': '',
        'slack_emote': '',
        'slack_shoutout': '',
        'slack_username': ''}

    yaml_config = (
        "---\n"
        "sites:\n"
        "- url: example.uk\n"
        "  status_code: 200\n"
        "- url: example.co.uk\n"
        "  status_code: 302\n"
        "domains:\n"
        "- domain: 8.8.8.8\n")

    yaml_config2 = (
        "---\n"
        "domains:\n"
        "- domain: 8.8.8.8\n"
        "sites:\n"
        "- url: example.fr\n"
        "  status_code: 200\n"
        "- url: example.com\n"
        "  status_code: 302\n")

    yaml_config3 = (
        "---\n"
        "domains:\n"
        "- domain: 8.8.8.8\n")

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

    yaml_config_no_url = (
        "---\n"
        "sites:\n"
        "- url: \n"
        "  status_code: 200\n")

    yaml_config_no_url2 = (
        "---\n"
        "sites:\n"
        "- status_code: 200\n")

    yaml_config_no_expected = (
        "---\n"
        "sites:\n"
        "- url: example.com\n"
        "  status_code: \n")

    yaml_config_no_expected2 = (
        "---\n"
        "sites:\n"
        "- url: example.com\n")

    yaml_config_malformed = (
        "aaaaaa\n"
        "--- bbbbb\n")

    yaml_config_malformed2 = (
        "---"
        "sites:"
        "- url: example.com"
        "  status_code: 200\n")

    yaml_config_malformed3 = (
        "---\n"
        "sites:\n"
        "  - url: http://example.co.uk\n"
        "  status_code: 200\n"
        "- url: http://example.org\n"
        "  status_code: 302\n"
        "domains:\n"
        "- domain: 8.8.8.8\n")

    yaml_config_no_suffix = (
        "---\n"
        "sites:\n"
        "- url: http://example\n"
        "  status_code: 200\n")

    yaml_config_redirect = (
        "---\n"
        "sites:\n"
        "- url: example.com\n"
        "  status_code: 302\n")

    yaml_config_redirect_multi = (
        "---\n"
        "sites:\n"
        "- url: example.com\n"
        "  status_code: 302\n"
        "- url: example.org\n"
        "  status_code: 301\n")

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_sites_config(self, mock_get_yaml_config, mock_slack):
        """Checks that a config file is correctly read in.
        """
        mock_get_yaml_config.side_effect = [yaml.load(self.yaml_config),
                                            self.slack_config]
        manager = MonitorManager()
        manager.parse_config()

        manager.check_domains()

        sites = manager.sites

        for site in sites:
            self.assertTrue(isinstance(site, MonitorSite))

        self.assertEqual(2, len(sites))
        self.assertEqual(0, mock_slack.call_count)

        self.assertEqual('example.uk', sites[0].url)
        self.assertEqual(200, sites[0].expected_status_code)

        self.assertEqual('example.co.uk', sites[1].url)
        self.assertEqual(302, sites[1].expected_status_code)

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_sites_config_reverse_input(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        mock_get_yaml_config.side_effect = [yaml.load(self.yaml_config2),
                                            self.slack_config]
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
        mock_get_yaml_config.side_effect = [yaml.load(self.yaml_config3),
                                            self.slack_config]
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
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config4), self.slack_config]
        mock_requests.side_effects = MissingSchema
        manager = MonitorManager()
        manager.parse_config()
        manager.check_sites()

        # Called twice because yaml_config4 has two sites in it
        self.assertEqual(2, mock_slack.call_count)

        # Part 2 with yaml_config5
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config5), self.slack_config]
        mock_requests.side_effects = MissingSchema
        manager = MonitorManager()
        manager.parse_config()
        manager.check_sites()

        # Called six times because yaml_config5 has four sites plus the
        #   previous two
        self.assertEqual(6, mock_slack.call_count)

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_site.get')
    @patch('monitor.monitor_manager.get_yaml_config')
    def test_site_without_suffix(self, mock_get_yaml_config, mock_requests,
                                 mock_slack):
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_no_suffix), self.slack_config]
        mock_requests.side_effects = ConnectionError
        manager = MonitorManager()
        manager.parse_config()
        manager.check_sites()

        self.assertEqual(1, mock_slack.call_count)

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    def test_site_with_expected_code_without_url(self, mock_get_yaml_config,
                                                 mock_slack):
        """If there is no url in the config, but there is an expected code then
        a slack alert should be sent to notify the config needs fixing.
        """
        # With a blank url:
        mock_get_yaml_config.side_effect = [yaml.load(self.yaml_config_no_url),
                                            self.slack_config]

        manager = MonitorManager()
        manager.parse_config()

        self.assertEqual([], manager.sites)
        self.assertEqual(1, mock_slack.call_count)

        # With url: missing completely
        mock_get_yaml_config.side_effect = [yaml.load(
            self.yaml_config_no_url2), self.slack_config]

        manager = MonitorManager()
        manager.parse_config()

        self.assertEqual([], manager.sites)
        self.assertEqual(2, mock_slack.call_count)

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_site_without_an_expected_status_code(self, mock_get_yaml_config):
        """If there is no expected status code in the config but there is a
        url, then 200 should be used as a default
        """
        # With status_code:
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_no_expected), self.slack_config]

        manager = MonitorManager()
        manager.parse_config()

        self.assertEqual(200, manager.sites[0].expected_status_code)

        # With status_code: missing completely
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_no_expected2), self.slack_config]

        manager = MonitorManager()
        manager.parse_config()

        self.assertEqual(200, manager.sites[0].expected_status_code)

    def test_read_blank_config(self):
        """Attempts to read from an empty config file
        """
        self.assertRaises(NoConfigFound, get_yaml_config, "")

    @patch('monitor.parse_yaml.open')
    def test_malformed_config_file_raises_composer_error(self, mock_open):
        """Attempts to read from a malformed config file
        """
        mock_open.return_value.__enter__.return_value = \
            self.yaml_config_malformed

        self.assertRaises(ComposerError, yaml.load, self.yaml_config_malformed)

        self.assertRaises(MalformedConfig, get_yaml_config)

    @patch('monitor.parse_yaml.open')
    def test_malformed_config_file_raises_scanner_error(self, mock_open):
        """Attempts to read from a malformed config file
        """
        mock_open.return_value.__enter__.return_value = \
            self.yaml_config_malformed2

        self.assertRaises(ScannerError, yaml.load, self.yaml_config_malformed2)

        self.assertRaises(MalformedConfig, get_yaml_config)

    @patch('monitor.parse_yaml.open')
    def test_malformed_config_file_raises_parser_error(self, mock_open):
        """Attempts to read from a malformed config file
        """
        mock_open.return_value.__enter__.return_value = \
            self.yaml_config_malformed3

        self.assertRaises(ParserError, yaml.load, self.yaml_config_malformed3)

        self.assertRaises(MalformedConfig, get_yaml_config)

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_code_expected_single(self, mock_requests,
            mock_get_yaml_config, mock_slack_post_message):
        """Test monitor manager doesn't send a message if the response status
        code matches the expected status code.
        """
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_single_site), self.slack_config]
        manager = MonitorManager()
        manager.parse_config()
        response_status_code = manager.sites[0].expected_status_code
        mock_requests.return_value.status_code = response_status_code
        manager.check_sites()

        mock_slack_post_message.assert_not_called()

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_code_unexpected_single(self, mock_requests,
            mock_get_yaml_config, mock_slack_post_message):
        """Test monitor manager sends a message if the response status
        code does not match the expected status code.
        """
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_single_site), self.slack_config]
        manager = MonitorManager()
        manager.parse_config()
        response_status_code = manager.sites[0].expected_status_code + 1
        mock_requests.return_value.status_code = response_status_code
        manager.check_sites()

        mock_slack_post_message.assert_called_once()

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_codes_expected_multiple(self,
                                            mock_requests,
                                            mock_get_yaml_config,
                                            mock_slack_post_message):
        """Test monitor manager doesn't send a message if the response status
        code matches the expected status code.
        """
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_multiple_sites), self.slack_config]

        manager = MonitorManager()
        manager.parse_config()
        response_status_code = manager.sites[0].expected_status_code
        mock_requests.return_value.status_code = response_status_code
        response_status_code = manager.sites[1].expected_status_code
        mock_requests.return_value.status_code = response_status_code

        manager.check_sites()

        mock_slack_post_message.assert_not_called()

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_codes_unexpected_multiple(self,
                                              mock_requests,
                                              mock_get_yaml_config,
                                              mock_slack_post_message):
        """Test monitor manager sends a message if the response status
        code does not match the expected status code.
        """
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_multiple_sites), self.slack_config]
        manager = MonitorManager()
        manager.parse_config()
        response_status_code = manager.sites[0].expected_status_code + 1
        mock_requests.get.return_value.status_code = response_status_code
        manager.check_sites()

        self.assertEqual(2, mock_slack_post_message.call_count)

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_code_redirect(self, mock_requests, mock_get_yaml_config,
                                  mock_slack_post_message):
        """Test monitor manager handles a successful redirection.
        """
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_redirect), self.slack_config]

        manager = MonitorManager()
        manager.parse_config()

        response_status_code = manager.sites[0].expected_status_code
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.history[0].status_code =\
            response_status_code

        manager.check_sites()

        mock_slack_post_message.assert_not_called()

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_code_redirect_multi(self, mock_requests,
                                        mock_get_yaml_config,
                                        mock_slack_post_message):
        """Test monitor manager handles a successful redirection.
        """
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_redirect), self.slack_config]

        manager = MonitorManager()
        manager.parse_config()

        response_status_code = manager.sites[0].expected_status_code
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.history[0].status_code =\
            response_status_code

        manager.check_sites()

        mock_slack_post_message.assert_not_called()

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_code_redirect_multi(self, mock_requests,
                                        mock_get_yaml_config,
                                        mock_slack_post_message):
        """Test monitor manager handles a successful redirection.
        """
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_redirect), self.slack_config]

        manager = MonitorManager()
        manager.parse_config()

        response_status_code = manager.sites[0].expected_status_code
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.history[0].status_code =\
            response_status_code

        manager.check_sites()

        mock_slack_post_message.assert_not_called()

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('monitor.monitor_site.get')
    def test_status_code_redirect_fail(self, mock_requests,
                                        mock_get_yaml_config,
                                        mock_slack_post_message):
        """Test monitor manager handles a successful redirection.
        """
        mock_get_yaml_config.side_effect = [
            yaml.load(self.yaml_config_redirect), self.slack_config]

        manager = MonitorManager()
        manager.parse_config()

        response_status_code = manager.sites[0].expected_status_code + 1
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.history[0].status_code =\
            response_status_code

        manager.check_sites()

        self.assertEqual(1, mock_slack_post_message.call_count)


class TestMonitorManagerDomains(unittest.TestCase):
    slack_config = {
        'slack_api_token': '',
        'slack_channel': '',
        'slack_emote': '',
        'slack_shoutout': '',
        'slack_username': ''}

    yaml_config_single = (
        "---\n"
        "domains:\n"
        "- domain: 8.8.8.8\n")

    yaml_config_multi = (
        "---\n"
        "domains:\n"
        "- domain: 8.8.8.8\n"
        "- domain: example.com\n"
        "- domain: example.org\n")

    yaml_config_no_domains = "---\n"


    yaml_config_malformed = (
        "---\n"
        "domains:\n"
        "  - domain: 8.8.8.8\n"
        "  - domain: example.com\n"
        "  - domain: example.org\n")

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    def test_domain(self, mock_get_yaml_config, mock_slack):
        mock_get_yaml_config.side_effect = [yaml.load(self.yaml_config_single),
                                            self.slack_config]
        manager = MonitorManager()
        manager.parse_config()

        domains = manager.domains

        for domain in domains:
            self.assertTrue(isinstance(domain, MonitorDomain))

        # 0 errors expected
        self.assertEqual(0, manager.check_domains())
        self.assertEqual(1, len(manager.domains))
        self.assertEqual(0, mock_slack.call_count)
        self.assertEqual('8.8.8.8', domains[0].url)

    @patch('monitor.monitor_manager.Slack.post_message')
    @patch('monitor.monitor_manager.get_yaml_config')
    def test_multiple_domains(self, mock_get_yaml_config, mock_slack):
        mock_get_yaml_config.side_effect = [yaml.load(self.yaml_config_multi),
                                            self.slack_config]
        manager = MonitorManager()
        manager.parse_config()

        # 0 errors expected
        self.assertEqual(0, manager.check_domains())
        self.assertEqual(3, len(manager.domains))
        self.assertEqual(0, mock_slack.call_count)

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_domains_config_with_no_domains(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        mock_get_yaml_config.side_effect = [yaml.load(
            self.yaml_config_no_domains), self.slack_config]
        manager = MonitorManager()
        manager.parse_config()

        domains = manager.domains

        self.assertEqual([], domains)


if __name__ == '__main__':
    unittest.main()
