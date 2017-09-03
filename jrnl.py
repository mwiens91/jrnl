#!/usr/bin/env python3
# coding: utf-8
"""Code description."""

import argparse
import os
import sys
import yaml

NAME = "jrnl"
VERSION = "0.0.0"
DESCRIPTION = "%(prog)s - GREAT PROGRAM A+"


def main():
    """Main program logic for jrnl."""
    # Parse runtime options
    parseRuntimeArguments()


def parseRuntimeArguments():
    """Parse runtime arguments using argparse.

    This will henerally return arguments as attributes, though some
    arguments will cause the program to exit.

    Returns:
        An object of type 'argparse.Namespace' containing the runtime
        arguments as attributes. See argparse documentation for more
        details.
    """
    parser = argparse.ArgumentParser(
            prog=NAME,
            description=DESCRIPTION,)

    parser.add_argument(
            "--setup",
            help="print configuration file and exit",
            nargs=0,
            action=PrintConfigAction)
    parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s" + VERSION)

    return parser.parse_args()


class PrintConfigAction(argparse.Action):
    """argparse action to print configuration file."""
    def __init__(self, option_strings, *args, **kwargs):
        super(PrintConfigAction, self).__init__(option_strings, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        # Build configuration file
        conf_dict = dict()
        conf_dict["editor"] = getUserEditor()
        conf_dict["journal_path"] = getUserJournalPath()

        # Print configuration file
        print("Save this configuration file in any of the following:")
        print("~/.jrnlrc\t~/.config/jrnl.conf\t$XDG_CONFIG_HOME/jrnl.conf")
        print()
        print("# jrnl config file")
        print(yaml.dump(conf_dict, default_flow_style=False))

        # Exit
        sys.exit(0)


def getUserEditor():
    """Return a string containing user's favourite editor."""
    # Try finding via an environment variable
    editorName = os.environ.get("EDITOR")

    if editorName:
        return editorName
    else:
        # Leave it to the user
        return "editor_name_here"


def getUserJournalPath():
    """Return a string containing user's journal path."""
    return os.path.expanduser("~/path/to/journal")


if __name__ == '__main__':
    # Run from command line
    main()
