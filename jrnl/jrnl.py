#!/usr/bin/env python3
# coding: utf-8
"""Main jrnl functionality."""

import datetime
import os
import subprocess
import sys
import dateutil.parser
from jrnl import grep_wrapper
from jrnl import helpers
from jrnl import runoptions


def main():
    """Main program for jrnl."""
    # Parse runtime options
    runtimeArgs = runoptions.parseRuntimeArguments()

    # Open up config file
    try:
        configDict = runoptions.getConfig()
    except runoptions.ConfigNotFoundException:
        print("No config file found!", file=sys.stderr)
        sys.exit(1)
    except runoptions.ConfigInvalidException:
        print("Config file invalid!", file=sys.stderr)
        sys.exit(1)

    # Use grep mode if requested
    try:
        if runtimeArgs.subparser_name == 'grep':
            grep_wrapper.grep_wrapper(runtimeArgs.pattern,
                                      configDict["journal_path"],
                                      extra_opts=runtimeArgs.options)
            sys.exit(0)
    except AttributeError:
        # Grep mode not requested
        pass

    # Make sure journal root directory exists
    if not os.path.isdir(configDict["journal_path"]):
        if helpers.prompt("Create '" + configDict["journal_path"] + "'?"):
            os.makedirs(configDict["journal_path"])
        else:
            sys.exit(0)

    # Figure out what editor to use
    if helpers.isProgramAvailable(configDict["editor"]):
        editorName = configDict["editor"]
    elif helpers.isProgramAvailable("sensible-editor"):
        editorName = "sensible-editor"
    else:
        print(configDict["editor"] + " not available!", file=sys.stderr)
        sys.exit(1)

    # Get today's datetime
    today = datetime.datetime.today()

    # Respect the "hours past midnight included in date" setting
    if today.hour < configDict["hours_past_midnight_included_in_date"]:
        latenight_date_offset = datetime.timedelta(days=-1)
    else:
        latenight_date_offset = datetime.timedelta()

    # Build datetime objects for the relevant dates
    if runtimeArgs.dates:
        # Parse dates given in runtime argument
        dates = []

        for datestring in runtimeArgs.dates:
            try:
                # Check for negative offsetting first
                offset = int(datestring)

                if offset > 0:
                    # Don't allow offseting from the future. Check if
                    # the argument passed in is a date instead
                    raise ValueError

                # Create datetime object using offset from current day
                dates.append(datetime.datetime.today()
                             + datetime.timedelta(days=offset)
                             + latenight_date_offset)
            except ValueError:
                try:
                    # Assume the date-string is a date, not an offset
                    dates.append(dateutil.parser.parse(datestring, fuzzy=True)
                                 + latenight_date_offset)
                except ValueError:
                    # The date given was not valid!
                    print("%s is not a valid date!" % datestring,
                          file=sys.stderr)

        if not dates:
            # No valid dates given
            print("No valid dates given! Aborting.", file=sys.stderr)
            sys.exit(1)
    else:
        # Use settings applicable when not specifying date
        dates = [today + latenight_date_offset]

    # Determine whether to write timestamp based on runtime args
    writetimestamp = (runtimeArgs.timestamp
                      or (configDict["write_timestamps_by_default"]
                          and not runtimeArgs.no_timestamp))

    # Determine whether to only open existing files
    readmode = (bool(runtimeArgs.dates)
                and not configDict["create_new_entries_when_specifying_dates"])

    # Open journal entries corresponding to the current date
    for date in dates:
        openEntry(date, editorName, configDict["journal_path"],
                  writetimestamp, readmode)

    # Exit
    sys.exit(0)


def writeTimestamp(entrypath, thisDatetime=datetime.datetime.today()):
    """Write timestamp to journal entry, if one doesn't already exist.

    Modifies a text file to include the passed in datetime's time and
    possibly date in ISO 8601 format. How this works depends on the file
    being created/modified:

    (1) If the journal entry text file doesn't already exist, create it
        and write the date and time to the top of the file.
    (2) If the journal entry already exists, look inside and see if
        the datetime's date is already written.  If the datetime's date
        is not written, append the date and time to the file, ensuring
        at least one empty line between the date and time and whatever
        text came before it.  If the datetime's date *is* written,
        follow the same steps as but omit writing the date; i.e., write
        only the time.

    Args:
        entrypath: A string containing a path to a journal entry,
            already created or not.
        thisDatetime: An optional datetime.datetime object representing
            today's date.
    """
    # Get strings for today's date and time
    thisDate = thisDatetime.strftime('%Y-%m-%d')
    thisTime = thisDatetime.strftime("%H:%M")

    # Check if journal entry already exists. If so write, the date and
    # time to it.
    if not os.path.isfile(entrypath):
        with open(entrypath, 'x') as jrnlentry:
            jrnlentry.write(thisDate + "\n" + thisTime + "\n")
    else:
        # Find if date already written
        entrytext = open(entrypath).read()

        if thisDate in entrytext:
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
                            + (thisDate + "\n") * printDate
                            + thisTime + "\n\n")


def openEntry(datetimeobj, editor, journalPath, dotimestamp, inreadmode,
              errorstream=sys.stderr):
    """Try opening a journal entry.

    Args:
        datetimeobj: A datetime.datetime object containing which day's
            journal entry to open.
        editor: A string containing the name of the editor to use.
        journalPath: A string containing the path to the journal's base
            directory.
        dotimestamp: A boolean signalling whether to append a timestamp
            to a journal entry before opening.
        inreadmode: A boolean signalling whether to only open existing
            entries ("read mode").
        errorstream: An optional TextIO object to send error messages
            to. Almost certainly you want to use the default standard
            error output.
    """

    # Determine path the journal entry text file
    yearDirPath = os.path.join(journalPath, str(datetimeobj.year))
    entryPath = os.path.join(yearDirPath, datetimeobj.strftime('%Y-%m-%d') + '.txt')

    # If in read mode, only open existing entries
    if inreadmode and not os.path.exists(entryPath):
        print("%s does not exist!" % entryPath, file=errorstream)
        return

    # Make the year directory if necessary
    if not os.path.isdir(yearDirPath):
        os.makedirs(yearDirPath)

    # Append timestamp to journal entry if necessary
    if dotimestamp:
        writeTimestamp(entryPath)

    # Open the date's journal
    subprocess.Popen([editor, entryPath]).wait()
