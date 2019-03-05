"""Contains functions relating to the config file."""

import os
import yaml
from .constants import CONFIG_KEYS


class ConfigNotFoundException(Exception):
    """An exception used specified config doesn't exist."""

    pass


class ConfigInvalidException(Exception):
    """An exception used specified config is invalid."""

    pass


def get_config():
    """Find and return config settings dictionary.

    Looks for config files located at

    ~/.jrnlrc
    ~/.config/jrnl.conf
    $XDG_CONFIG_HOME/jrnl.conf

    Returns:
        If a valid config file can be found, returns a dictionary
        containing config settings.

    Raises:
        ConfigNotFoundException: A config file could not be found.
        ConfigInvalidException: A config file was found to be invalid.
    """
    # Build list of possible config files
    possible_configs = [
        os.path.expanduser("~/.jrnlrc"),
        os.path.expanduser("~/.config/jrnl.conf"),
    ]

    # Also look in XDG dirs, provided they exist
    if os.environ.get("XDG_CONFIG_HOME"):
        possible_configs += [os.environ.get("XDG_CONFIG_HOME") + "/jrnl.conf"]

    # Iterate through all possible config files
    for config_path in possible_configs:
        if os.path.isfile(config_path):
            with open(config_path, "r") as config_file:
                # Try loading the config file
                try:
                    config_dict = yaml.safe_load(config_file)
                except yaml.YAMLError:
                    # Bad config file
                    raise ConfigInvalidException

                # Verify the config file contains required options
                if CONFIG_KEYS.issubset(set(config_dict.keys())):
                    return config_dict

                # Required option(s) not specified
                raise ConfigInvalidException

    # None of earlier config files checked out
    raise ConfigNotFoundException
