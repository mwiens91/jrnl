"""Main jrnl module."""

import datetime
import os
import sys
import dateutil.parser
from .config import ConfigInvalidException, ConfigNotFoundException, get_config
from .grep_wrapper import grep_wrapper
from .helpers import is_program_available, prompt
from .journal import open_entry
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
                config_dict["journal_path"],
                extra_opts=runtime_args.options,
            )
            sys.exit(0)
    except AttributeError:
        # Grep mode not requested
        pass

    # Make sure journal root directory exists
    if not os.path.isdir(config_dict["journal_path"]):
        if prompt("Create '" + config_dict["journal_path"] + "'?"):
            os.makedirs(config_dict["journal_path"])
        else:
            sys.exit(0)

    # Figure out what editor to use
    if is_program_available(config_dict["editor"]):
        editor_name = config_dict["editor"]
    elif is_program_available("sensible-editor"):
        editor_name = "sensible-editor"
    else:
        print(config_dict["editor"] + " not available!", file=sys.stderr)
        sys.exit(1)

    # Get today's datetime
    today = datetime.datetime.today()

    # Respect the "hours past midnight included in date" setting
    if today.hour < config_dict["hours_past_midnight_included_in_date"]:
        latenight_date_offset = datetime.timedelta(days=-1)
    else:
        latenight_date_offset = datetime.timedelta()

    # Build datetime objects for the relevant dates
    if runtime_args.dates:
        # Parse dates given in runtime argument
        dates = []

        for datestring in runtime_args.dates:
            try:
                # Check for negative offsetting first
                offset = int(datestring)

                if offset > 0:
                    # Don't allow offseting from the future. Check if
                    # the argument passed in is a date instead
                    raise ValueError

                # Create datetime object using offset from current day
                dates.append(
                    datetime.datetime.today()
                    + datetime.timedelta(days=offset)
                    + latenight_date_offset
                )
            except ValueError:
                try:
                    # Assume the date-string is a date, not an offset
                    dates.append(
                        dateutil.parser.parse(datestring, fuzzy=True)
                        + latenight_date_offset
                    )
                except ValueError:
                    # The date given was not valid!
                    print(
                        "%s is not a valid date!" % datestring, file=sys.stderr
                    )

        if not dates:
            # No valid dates given
            print("No valid dates given! Aborting.", file=sys.stderr)
            sys.exit(1)
    else:
        # Use settings applicable when not specifying date
        dates = [today + latenight_date_offset]

    # Determine whether to write timestamp based on runtime args
    writetimestamp = runtime_args.timestamp or (
        config_dict["write_timestamps_by_default"]
        and not runtime_args.no_timestamp
    )

    # Determine whether to only open existing files
    readmode = (
        bool(runtime_args.dates)
        and not config_dict["create_new_entries_when_specifying_dates"]
    )

    # Open journal entries corresponding to the current date
    for date in dates:
        open_entry(
            date,
            editor_name,
            config_dict["journal_path"],
            writetimestamp,
            readmode,
        )

    # Exit
    sys.exit(0)
