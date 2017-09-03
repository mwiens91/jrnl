#!/usr/bin/env python3
# coding: utf-8
"""Source code for jrnl."""

import argparse
import datetime
import os
import sys
import yaml

NAME = "jrnl"
VERSION = "0.0.0"
DESCRIPTION = "%(prog)s - write a journal"


def main():
    """Main program for jrnl."""
    # Parse runtime options
    parseRuntimeArguments()

    # Open up config file
    configDict = getConfig()

    if not configDict:
        print("No config file found!", file=sys.stderr)
        sys.exit(1)

    # Figure out what editor to use
    if isProgramAvailable(configDict["editor"]):
        editorName = configDict["editor"]
    elif isProgramAvailable("sensible-editor"):
        editorName = "sensible-editor"
    else:
        print(configDict["editor"] + " not available!", file=sys.stderr)

    # Make sure journal root directory exists
    if not os.path.isdir(configDict["journal_path"]):
        if input("Create '" + configDict["journal_path"] + "'?"):
            os.makedirs(configDict["journal_path"])
        else:
            return None

    # By this point assume journal directory exists
    # Find day entry to open, using previous day if hour early enough
    today = datetime.datetime.today()
    if today.hour < conf_dict["hours_past_midnight_included_in_day"]:
        today = today - datetime.timedelta(days=1)

    # Make the year directory if necessary
    yearDirPath = os.path.join(configDict["journal_path"], str(today.year))
    if not os.path.isdir(yearDirPath):
        os.makedirs(yearDirPath)

    # Open today's journal


def parseRuntimeArguments():
    """Parse runtime arguments using argparse.

    This will generally return arguments as attributes, though some
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
            version="%(prog)s " + VERSION)

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
        conf_dict["hours_past_midnight_included_in_day"] = 4

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
    # Iterate through all possible config files
    for configpath in [os.path.expanduser("~/.jrnlrc"),
                       os.path.expanduser("~/.config/jrnl.conf"),
                       os.environ.get("XDG_CONFIG_HOME") + "/jrnl.conf",]:
        if os.path.isfile(configpath):
            with open(configpath, "r") as configfile:
                try:
                    return yaml.load(configfile)
                except yaml.YAMLError as exc:
                    # Something bad happened
                    print(exc, file=sys.stderr)
                    break

    # None of earlier config files checked out
    return None


def isProgramAvailable(programName):
    """Find if program passed in is available.

    Arg:
        programName: A string containing a program name.
    Returns:
        A boolean specifying whether the program specified is available.
    """
    return not subprocess.Popen(["bash", "-c", "type " + programName],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL).wait()


if __name__ == '__main__':
    # Run from command line
    main()
