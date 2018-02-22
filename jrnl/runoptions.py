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
    # Annoyingly, subparsers and the dates argument don't work nicely
    # together - order matters. If using grep, add subparser support
    # first.  Otherwise, add the subparser support after.
    if len(sys.argv) > 1 and sys.argv[1] == 'grep':
        GIVE_GREP_PRIORITY = True
    else:
        GIVE_GREP_PRIORITY = False

    # A function to add subparser support
    def addSubParsers(parser_):
        """Add subparser support for sub-commands.
        Arg:
            parser_: An argparse.ArgumentParser

        Returns:
            An argparse._SubParsersAction subparsers . . . thing?
        """
        return parser_.add_subparsers(dest="subparser_name", title="commands")

    # Instantiate the parser
    parser = argparse.ArgumentParser(
            prog=NAME,
            description="%(prog)s - " + DESCRIPTION,)

    # Give subparser support first if using grep
    if GIVE_GREP_PRIORITY:
        subparsers = addSubParsers(parser)

    # Continue as normal
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

    # Give subparser support if we haven't done so already
    if not GIVE_GREP_PRIORITY:
        subparsers = addSubParsers(parser)

    # Add grep subcommand
    grep_parser = subparsers.add_parser(
            "grep",
            help=("print lines from a time span matching a pattern."
                  " Will accept any grep options."))
    grep_parser.add_argument(
            "pattern",
            help="search pattern",)
    grep_parser.add_argument(
            "-y", "--years",
            help="which years' entries to search in",
            nargs="+",)

    # Parse args and add grep options in if existing
    namespace, extras = parser.parse_known_args()
    namespace.options = extras

    return namespace


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
