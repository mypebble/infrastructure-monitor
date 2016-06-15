#!/usr/bin/env python
from yaml import load
from yaml.composer import ComposerError
from yaml.scanner import ScannerError
from yaml.parser import ParserError


def get_yaml_config(config_file=None):
    try:
        with open(config_file, 'r') as yaml_file:
            return load(yaml_file)
    except IOError:
        raise NoConfigFound
    except (ComposerError, ParserError, ScannerError):
        raise MalformedConfig


class MalformedConfig(Exception):
    def __init__(self):
        super(MalformedConfig, self).__init__(
            "A malformed config file has been found. Please check the "
            "formatting of your config.yaml file.")


class NoConfigFound(Exception):
    def __init__(self):
        super(NoConfigFound, self).__init__(
            "No config file has been found. Please ensure you have a "
            "config.yaml file and it is correctly formatted.")
