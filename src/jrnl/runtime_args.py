"""Contains functions relating to parsing runtime args."""

import argparse
import os
import sys
import yaml
from .constants import (
    EDITOR,
    JOURNAL_PATH,
    HOURS_PAST_MIDNIGHT_INCLUDED_IN_DATE,
    CREATE_NEW_ENTRIES_WHEN_SPECIFYING_DATES,
    WRITE_TIMESTAMPS_BY_DEFAULT,
)
from .helpers import get_user_editor
from .version import DESCRIPTION, NAME, VERSION


class PrintConfigAction(argparse.Action):
    """argparse action to print configuration file and exit."""

    def __call__(self, parser, namespace, values, option_string=None):
        # Build configuration file
        confdict = dict()
        confdict[EDITOR] = get_user_editor()
        confdict[JOURNAL_PATH] = os.path.expanduser("~/path/to/journal")
        confdict[HOURS_PAST_MIDNIGHT_INCLUDED_IN_DATE] = 4
        confdict[CREATE_NEW_ENTRIES_WHEN_SPECIFYING_DATES] = False
        confdict[WRITE_TIMESTAMPS_BY_DEFAULT] = True

        # Print configuration file
        print("# jrnl config file")
        print("# Save this configuration file in any of the following:")
        print("# ~/.jrnlrc\t~/.config/jrnl.conf\t$XDG_CONFIG_HOME/jrnl.conf")
        print("#")
        print(
            "# '" + HOURS_PAST_MIDNIGHT_INCLUDED_IN_DATE + "' is the number of"
        )
        print("# hours into the next date a date's journal entries should")
        print("# cover. Example: say this setting is set to 4. Then if it")
        print("# was 03:00 on 2018-03-03, jrnl would open up 2018-03-02's")
        print("# journal entries")
        print()
        print(yaml.dump(confdict, default_flow_style=False))

        # Exit
        sys.exit(0)


def parse_runtime_arguments():
    """Parse runtime arguments using argparse.

    This will generally return runtime arguments as attributes, though
    some runtime arguments will cause the program to exit.

    Returns:
        An object of type 'argparse.Namespace' containing the runtime
        arguments as attributes. See argparse documentation for more
        details.
    """
    # Annoyingly, subparsers and the dates argument don't work nicely
    # together - order matters. If using grep, add subparser support.
    give_grep_priority = bool(len(sys.argv) > 1 and sys.argv[1] == "grep")

    # A function to add subparser support
    def add_subparsers(parser_):
        """Add subparser support for sub-commands.

        Args:
            parser_: An argparse.ArgumentParser

        Returns:
            An argparse._SubParsersAction subparsers . . . thing?
        """
        return parser_.add_subparsers(dest="subparser_name", title="commands")

    # Instantiate the parser
    parser = argparse.ArgumentParser(
        prog=NAME, description="%(prog)s - " + DESCRIPTION
    )

    # Give subparser support if using grep
    if give_grep_priority:
        subparsers = add_subparsers(parser)

        # Add grep subcommand
        grep_parser = subparsers.add_parser(
            "grep",
            description=(
                "%(prog)s - "
                "print lines from a time span matching a pattern."
                " Will accept all grep options (which are not "
                " listed here);"
                " see 'man grep' for more details."
            ),
            help=(
                "print lines from a time span matching a pattern."
                " Will accept any grep options."
            ),
        )
        grep_parser.add_argument("pattern", help="search pattern")
    else:
        # Continue as normal
        parser.add_argument(
            "dates",
            help=("journal date(s) to open." " Defaults to right now."),
            nargs="*",
        )
        parser.add_argument("-e", "--editor", help="editor to use")
        parser.add_argument(
            "--setup",
            help="print configuration file and exit",
            nargs=0,
            action=PrintConfigAction,
        )
        parser.add_argument(
            "--version", action="version", version="%(prog)s " + VERSION
        )
        timestamp_option = parser.add_mutually_exclusive_group()
        timestamp_option.add_argument(
            "-t",
            "--timestamp",
            help="write a timestamp before opening editor",
            action="store_true",
        )
        timestamp_option.add_argument(
            "--no-timestamp",
            help="don't write a timestamp before opening editor",
            action="store_true",
        )

    # This looks needlessly complicated, but it's necessary to pass in
    # arbitrary options into grep
    namespace, extras = parser.parse_known_args()
    namespace.options = extras

    return namespace
