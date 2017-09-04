#!/usr/bin/env python3
# coding: utf-8
"""Source code for jrnl."""

import argparse
import datetime
import distutils.util
import os
import subprocess
import sys
import yaml

NAME = "jrnl"
PYPINAME = "jrnl-mw"
VERSION = "0.0.6"
DESCRIPTION = "write a journal"


def main():
    """Main program for jrnl."""
    # Parse runtime options
    runtimeArgs = parseRuntimeArguments()

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
        if prompt("Create '" + configDict["journal_path"] + "'?"):
            os.makedirs(configDict["journal_path"])
        else:
            sys.exit(1)

    # By this point assume journal directory exists
    # Find day entry to open, using previous day if hour early enough
    today = datetime.datetime.today()
    if today.hour < configDict["hours_past_midnight_included_in_day"]:
        today = today - datetime.timedelta(days=1)

    # Make the year directory if necessary
    yearDirPath = os.path.join(configDict["journal_path"], str(today.year))
    if not os.path.isdir(yearDirPath):
        os.makedirs(yearDirPath)

    # Append timestamp to journal entry if necessary
    entryPath = os.path.join(yearDirPath, today.strftime('%Y-%m-%d') + '.txt')

    if (configDict["write_timestamp"] and not runtimeArgs.no_timestamp) or (
            runtimeArgs.timestamp):
        writeTimestamp(entryPath)

    # Open today's journal
    subprocess.Popen([editorName, entryPath]).wait()

    # Exit
    sys.exit(0)


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
            description="%(prog)s - " + DESCRIPTION,)

    parser.add_argument(
            "--setup",
            help="print configuration file and exit",
            nargs=0,
            action=PrintConfigAction)
    parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s " + VERSION)
    timestamp_option = parser.add_mutually_exclusive_group()
    timestamp_option.add_argument(
            "-t", "--timestamp",
            help="write a timestamp before opening editor",
            action="store_true")
    timestamp_option.add_argument(
            "--no-timestamp",
            help="don't write a timestamp before opening editor",
            action="store_true")

    return parser.parse_args()


class PrintConfigAction(argparse.Action):
    """argparse action to print configuration file and exit."""
    def __init__(self, option_strings, *args, **kwargs):
        super(PrintConfigAction, self).__init__(option_strings, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        # Build configuration file
        confdict = dict()
        confdict["editor"] = getUserEditor()
        confdict["hours_past_midnight_included_in_day"] = 4
        confdict["journal_path"] = getUserJournalPath()
        confdict["write_timestamp"] = True

        # Print configuration file
        print("# jrnl config file")
        print("# Save this configuration file in any of the following:")
        print("# ~/.jrnlrc\t~/.config/jrnl.conf\t$XDG_CONFIG_HOME/jrnl.conf")
        print()
        print(yaml.dump(confdict, default_flow_style=False))

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
    # Build list of possible config files
    possibleConfigs = [os.path.expanduser("~/.jrnlrc"),
                       os.path.expanduser("~/.config/jrnl.conf"),]

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


def prompt(query):
    """Prompt a yes/no question and get an answer.

    A simple function to ask yes/no questions on the command line.
    Credit goes to Matt Stevenson. See:
    http://mattoc.com/python-yes-no-prompt-cli.html

    Args:
        query: A string containing a question.

    Returns:
        A boolean corresponding to the answer to the question asked.
    """
    sys.stdout.write("%s [y/n]: " % query)
    val = input().lower()
    try:
        result = distutils.util.strtobool(val)
    except ValueError:
        # Result no good! Ask again.
        sys.stdout.write("Please answer with y/n\n")
        return prompt(query)
    return result


def writeTimestamp(entrypath, todayDatetime=datetime.datetime.today()):
    """Write timestamp to journal entry, if one doesn't already exist.

    Modifies a text file to include today's time and possibly date in
    ISO 8601. How this works depends on the file being created/modified:

    (1) If the journal entry text file doesn't already exist, create it
        and write the date and time to the top of the file.
    (2) If the journal entry already exists, look inside and see if
        today's date is already written.  If today's date is not
        written, write the date and time to the bottom of the file,
        ensuring at least one empty line between the date and time and
        whatever text came before it.  If today's date is written,
        follow the same steps as if the date isn't written, but omit
        writing the date; i.e., write only the time.

    Args:
        entrypath: A string containing a path to a journal entry,
            already created or not.
        todayDatetime: An optional datetime.datetime object representing
            today's date.
    """
    # Get strings for today's date and time
    todayDate = todayDatetime.strftime('%Y-%m-%d')
    todayTime = todayDatetime.strftime("%H:%M")

    # Check if journal entry already exists. If so write, the date and
    # time to it.
    if not os.path.isfile(entrypath):
        with open(entrypath, 'x') as jrnlentry:
            jrnlentry.write(todayDate + "\n" + todayTime + "\n")
    else:
        # Find if date already written
        entrytext = open(entrypath).read()

        if todayDate in entrytext:
            printDate = False
        else:
            printDate = True

        # Find if we need to insert a newline at the bottom of the file
        if entrytext.endswith("\n\n"):
            printNewLine = False
        else:
            printNewLine = True

        # Write to the file
        with open(entrypath, 'a') as jrnlentry:
            jrnlentry.write(printNewLine * "\n"
                            + (todayDate + "\n") * printDate
                            + todayTime + "\n\n")


if __name__ == '__main__':
    # Run from command line
    try:
        main()
    except KeyError:
        print("Please update config file!", file=sys.stderr)
