import unittest
import yaml

from mock import Mock, patch

from monitor_manager import MonitorManager, Site


class TestParseConfig(unittest.TestCase):
    yaml_config = "---\n"\
                  "sites:\n"\
                  "- url: example.uk\n"\
                  "  status_code: 200\n"\
                  "- url: example.co.uk\n"\
                  "  status_code: 302\n"\
                  "domains:\n"\
                  "- url: 8.8.8.8\n"

    yaml_config2 = "---\n" \
                   "domains:\n" \
                   "- url: 8.8.8.8\n" \
                   "sites:\n" \
                   "- url: example.uk\n" \
                   "  status_code: 200\n" \
                   "- url: example.co.uk\n" \
                   "  status_code: 302\n" \


    @patch('monitor_manager.MonitorManager.get_yaml_config')
    def test_read_sites_from_config(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config)
        monitor_manager = MonitorManager()

        sites = monitor_manager.sites

        for site in sites:
            self.assertTrue(isinstance(site, Site))

        self.assertEqual(sites[0].url, 'example.uk')
        self.assertEqual(sites[0].expected_status_code, 200)

        self.assertEqual(sites[1].url, 'example.co.uk')
        self.assertEqual(sites[1].expected_status_code, 302)

        # Using yaml_config2
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config2)
        monitor_manager = MonitorManager()

        sites = monitor_manager.sites

        for site in sites:
            self.assertTrue(isinstance(site, Site))

        self.assertEqual(sites[0].url, 'example.uk')
        self.assertEqual(sites[0].expected_status_code, 200)

        self.assertEqual(sites[1].url, 'example.co.uk')
        self.assertEqual(sites[1].expected_status_code, 302)

    @patch('monitor_manager.MonitorManager.get_yaml_config')
    def test_read_sites_from_blank_config(self, mock_get_yaml_config):
        """Attempts to read from an empty config file
        """
        mock_get_yaml_config.return_value = yaml.load("")
        monitor_manager = MonitorManager()

        sites = monitor_manager.sites

        self.assertEqual(sites, [])

    @patch('monitor_manager.MonitorManager.get_yaml_config')
    def test_read_domains_from_config(self, mock_get_yaml_config):
        """Checks that a config file is correctly read in.
        """
        # Using yaml_config
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config)
        monitor_manager = MonitorManager()

        domains = monitor_manager.domains

        for domain in domains:
            self.assertTrue(isinstance(domain, str))

        self.assertEqual(domains[0], '8.8.8.8')

        # Using yaml_config2
        mock_get_yaml_config.return_value = yaml.load(self.yaml_config)
        monitor_manager = MonitorManager()

        domains = monitor_manager.domains

        for domain in domains:
            self.assertTrue(isinstance(domain, str))

        self.assertEqual(domains[0], '8.8.8.8')

    @patch('monitor_manager.MonitorManager.get_yaml_config')
    def test_read_domains_from_blank_config(self, mock_get_yaml_config):
        """Attempts to read from an empty config file
        """
        mock_get_yaml_config.return_value = yaml.load("")
        monitor_manager = MonitorManager()

        domains = monitor_manager.domains

        self.assertEqual(domains, [])

if __name__ == '__main__':
    unittest.main()
