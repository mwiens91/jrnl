"""Main jrnl module."""

import datetime
import os
import sys
from .config import ConfigInvalidException, ConfigNotFoundException, get_config
from .constants import (
    EDITOR,
    JOURNAL_PATH,
    HOURS_PAST_MIDNIGHT_INCLUDED_IN_DATE,
    CREATE_NEW_ENTRIES_WHEN_SPECIFYING_DATES,
    WRITE_TIMESTAMPS_BY_DEFAULT,
)
from .grep_wrapper import grep_wrapper
from .helpers import is_program_available, prompt
from .journal import open_entry, parse_dates
from .runtime_args import parse_runtime_arguments


def main():
    """Main program for jrnl."""
    # Parse runtime options
    runtime_args = parse_runtime_arguments()

    # Open up config file
    try:
        config_dict = get_config()
    except ConfigNotFoundException:
        print("No config file found!", file=sys.stderr)
        sys.exit(1)
    except ConfigInvalidException:
        print("Config file invalid!", file=sys.stderr)
        sys.exit(1)

    # Use grep mode if requested
    try:
        if runtime_args.subparser_name == "grep":
            grep_wrapper(
                runtime_args.pattern,
                config_dict[JOURNAL_PATH],
                extra_opts=runtime_args.options,
            )
            sys.exit(0)
    except AttributeError:
        # Grep mode not requested
        pass

    # Make sure journal root directory exists
    if not os.path.isdir(config_dict[JOURNAL_PATH]):
        if prompt("Create '" + config_dict[JOURNAL_PATH] + "'?"):
            os.makedirs(config_dict[JOURNAL_PATH])
        else:
            sys.exit(0)

    # Figure out what editor to use
    if runtime_args.editor is not None:
        editor_name = runtime_args.editor
    elif is_program_available(config_dict[EDITOR]):
        editor_name = config_dict[EDITOR]
    elif is_program_available("sensible-editor"):
        editor_name = "sensible-editor"
    else:
        print(config_dict[EDITOR] + " not available!", file=sys.stderr)
        sys.exit(1)

    # Get today's datetime
    today = datetime.datetime.today()

    # Respect the "hours past midnight included in date" setting
    if today.hour < config_dict[HOURS_PAST_MIDNIGHT_INCLUDED_IN_DATE]:
        latenight_date_offset = datetime.timedelta(days=-1)
    else:
        latenight_date_offset = datetime.timedelta()

    # Build datetime.date objects for the relevant dates
    if runtime_args.dates:
        # Parse dates given in runtime argument
        dates = parse_dates(
            runtime_args.dates,
            latenight_date_offset,
            config_dict[JOURNAL_PATH],
        )

        if not dates:
            # No valid dates given
            print("No valid dates given! Aborting.", file=sys.stderr)
            sys.exit(1)
    else:
        # Use settings applicable when not specifying date
        dates = [today.date() + latenight_date_offset]

    # Determine whether to write timestamp based on runtime args
    write_timestamp = runtime_args.timestamp or (
        config_dict[WRITE_TIMESTAMPS_BY_DEFAULT]
        and not runtime_args.no_timestamp
    )

    # Determine whether to only open existing files
    read_mode = (
        bool(runtime_args.dates)
        and not config_dict[CREATE_NEW_ENTRIES_WHEN_SPECIFYING_DATES]
    )

    # Open journal entries corresponding to the current date
    for date in dates:
        open_entry(
            date,
            editor_name,
            config_dict[JOURNAL_PATH],
            write_timestamp,
            read_mode,
        )

    # Exit
    sys.exit(0)
