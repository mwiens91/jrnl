"""Contains functions relating to config and runtime args."""

import argparse
import os
import sys
import yaml
from jrnl import helpers
from jrnl.version import DESCRIPTION, NAME, VERSION


class ConfigException(Exception):
    """An exception used when loading config fails."""
    pass


class PrintConfigAction(argparse.Action):
    """argparse action to print configuration file and exit."""
    def __call__(self, parser, namespace, values, option_string=None):
        # Build configuration file
        confdict = dict()
        confdict["editor"] = helpers.getUserEditor()
        confdict["hours_past_midnight_included_in_today"] = 4
        confdict["journal_path"] = os.path.expanduser("~/path/to/journal")
        confdict["open_new_entries_for_other_days"] = False
        confdict["write_timestamp_for_other_days"] = False
        confdict["write_timestamp_for_today"] = True

        # Print configuration file
        print("# jrnl config file")
        print("# Save this configuration file in any of the following:")
        print("# ~/.jrnlrc\t~/.config/jrnl.conf\t$XDG_CONFIG_HOME/jrnl.conf")
        print("#")
        print("# 'today' is a date (today) when running with no arguments")
        print(("# 'other day' means a day, possibly even today"
               " when running with specific date arguments"))
        print()
        print(yaml.dump(confdict, default_flow_style=False))

        # Exit
        sys.exit(0)


def parseRuntimeArguments():
    """Parse runtime arguments using argparse.

    This will generally return runtime arguments as attributes, though
    some runtime arguments will cause the program to exit.

    Returns:
        An object of type 'argparse.Namespace' containing the runtime
        arguments as attributes. See argparse documentation for more
        details.
    """
    parser = argparse.ArgumentParser(
            prog=NAME,
            description="%(prog)s - " + DESCRIPTION,)
    parser.add_argument(
            "dates",
            help=("journal date(s) to open ('-1', '-2'-offsetting allowed)."
                 " Defaults to right now."),
            nargs="*",)
    parser.add_argument(
            "--setup",
            help="print configuration file and exit",
            nargs=0,
            action=PrintConfigAction,)
    parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s " + VERSION,)
    timestamp_option = parser.add_mutually_exclusive_group()
    timestamp_option.add_argument(
            "-t", "--timestamp",
            help="write a timestamp before opening editor",
            action="store_true",)
    timestamp_option.add_argument(
            "--no-timestamp",
            help="don't write a timestamp before opening editor",
            action="store_true",)

    # Parser for sub-commands
    subparsers = parser.add_subparsers()

    # Sub-command for grep wrapper
    grep_parser = subparsers.add_parser("grep", help="grep wrapper")
    grep_parser.add_argument(
            "time span",
            help="year, month, or day to grep over",
            nargs="*",)

    return parser.parse_args()


def getConfig():
    """Find and return config settings dictionary.

    Looks for config files located at

    ~/.jrnlrc
    ~/.config/jrnl.conf
    $XDG_CONFIG_HOME/jrnl.conf

    Returns:
        If a config setting can be found, returns a dictionary
        containing config settings; otherwise returns None.
    """
    # Build list of possible config files
    possibleConfigs = [os.path.expanduser("~/.jrnlrc"),
                       os.path.expanduser("~/.config/jrnl.conf"),]

    # Also look in XDG dirs, provided they exist
    if os.environ.get("XDG_CONFIG_HOME"):
        possibleConfigs += [os.environ.get("XDG_CONFIG_HOME") + "/jrnl.conf",]

    # Iterate through all possible config files
    for configpath in possibleConfigs:
        if os.path.isfile(configpath):
            with open(configpath, "r") as configfile:
                try:
                    return yaml.load(configfile)
                except yaml.YAMLError as exc:
                    # Something bad happened
                    print(exc, file=sys.stderr)
                    break

    # None of earlier config files checked out
    raise ConfigException
