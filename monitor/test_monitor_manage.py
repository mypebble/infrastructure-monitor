import unittest
import yaml

from mock import patch

from monitor.monitor_manager import MonitorManager, Site, NoConfigFound
from slack.slack import Slack


class TestParseConfig(unittest.TestCase):
    yaml_config = "---\n" \
                  "sites:\n" \
                  "- url: example.uk\n" \
                  "  status_code: 200\n" \
                  "- url: example.co.uk\n" \
                  "  status_code: 302\n" \
                  "domains:\n" \
                  "- url: 8.8.8.8\n"

    yaml_config2 = "---\n" \
                   "domains:\n" \
                   "- url: 8.8.8.8\n" \
                   "sites:\n" \
                   "- url: example.fr\n" \
                   "  status_code: 200\n" \
                   "- url: example.com\n" \
                   "  status_code: 302\n"

    yaml_config3 = "---\n" \
                   "domains:\n" \
                   "- url: 8.8.8.8\n"

    yaml_config4 = "---\n" \
                   "sites:\n" \
                   "- url: example.fr\n" \
                   "  status_code: 200\n" \
                   "- url: example.com\n" \
                   "  status_code: 302\n"

    yaml_config_single_site = "---\n" \
                              "sites:\n" \
                              "- url: example.com" \
                              "  status_code: 200"

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_sites_from_config(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config)
        monitor_manager = MonitorManager()
        monitor_manager.parse_config()

        sites = monitor_manager.sites

        for site in sites:
            self.assertTrue(isinstance(site, Site))

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
        monitor_manager = MonitorManager()
        monitor_manager.parse_config()

        sites = monitor_manager.sites

        for site in sites:
            self.assertTrue(isinstance(site, Site))

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
        monitor_manager = MonitorManager()
        monitor_manager.parse_config()

        sites = monitor_manager.sites

        self.assertEqual([], sites)

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_sites_from_blank_config(self, mock_get_yaml_config):
        """Attempts to read from an empty config file. NoConfigFound
        exception should be thrown.
        """
        mock_get_yaml_config.return_value = yaml.load("")
        monitor_manager = MonitorManager()

        sites = monitor_manager.sites
        self.assertEqual([], sites)

        self.assertRaises(NoConfigFound, monitor_manager.parse_config())

        sites = monitor_manager.sites
        self.assertEqual([], sites)

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_domains_from_config(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config)
        monitor_manager = MonitorManager()
        monitor_manager.parse_config()

        domains = monitor_manager.domains

        for domain in domains:
            self.assertTrue(isinstance(domain, str))

        self.assertEqual(domains[0], '8.8.8.8')

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_domains_from_config_reverse_input(self, mock_get_yaml_config):
        # Using yaml_config2
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config2)
        monitor_manager = MonitorManager()
        monitor_manager.parse_config()

        domains = monitor_manager.domains

        for domain in domains:
            self.assertTrue(isinstance(domain, str))

        self.assertEqual('8.8.8.8', domains[0])

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_domains_from_config_with_only_sites(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config4)
        monitor_manager = MonitorManager()
        monitor_manager.parse_config()

        domains = monitor_manager.domains

        self.assertEqual([], domains)

    @patch('monitor.monitor_manager.get_yaml_config')
    def test_read_domains_from_blank_config(self, mock_get_yaml_config):
        """Attempts to read from an empty config file
        """
        mock_get_yaml_config.return_value = yaml.load("")
        monitor_manager = MonitorManager()

        domains = monitor_manager.domains
        self.assertEqual([], domains)

        self.assertRaises(NoConfigFound, monitor_manager.parse_config())

        domains = monitor_manager.domains
        self.assertEqual([], domains)

    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('slack.slack.Slack.post_message')
    def test_expected_status_code(self, mock_slack_post_message, mock_get_yaml_config):
        """Test monitor manager doesn't send a message if the response status
        code matches the expected status code.
        """
        mock_get_yaml_config.return_value = yaml.load("")
        monitor_manager = MonitorManager()
        monitor_manager.parse_config()
        monitor_manager.check_sites()

        mock_slack_post_message.assert_not_called()

    @patch('monitor.monitor_manager.get_yaml_config')
    @patch('slack.slack.Slack.post_message')
    def test_unexpected_status_code(self, mock_slack_post_message, mock_get_yaml_config):
        """Test monitor manager sends a message if the response status
        code does not match the expected status code.
        """
        mock_get_yaml_config.return_value = yaml.load("")
        monitor_manager = MonitorManager()
        monitor_manager.parse_config()
        monitor_manager.check_sites()

        mock_slack_post_message.assert_not_called()


if __name__ == '__main__':
    unittest.main()
