"""Contains functions relating to opening journal entries."""

import datetime
import os
import subprocess
import sys
import dateutil.parser


def parse_dates(date_args, late_night_date_offset):
    """Parse dates given in runtime arguments.

    Args:
        date_args: A list of strings containing date arguments to be
            parsed
        late_night_date_offset: A datetime.timedelta specifying how many
            hours to adjust each date.

    Returns:
        A list of datetime.datetimes representing the journal dates to
        open.
    """
    # Parse dates given in runtime argument
    parsed_dates = []

    for date_string in date_args:
        try:
            # Check for negative offsetting first
            offset = int(date_string)

            if offset > 0:
                # Don't allow offseting from the future. Check if
                # the argument passed in is a date instead
                raise ValueError

            # Create datetime object using offset from current day
            parsed_dates.append(
                datetime.datetime.today()
                + datetime.timedelta(days=offset)
                + late_night_date_offset
            )
        except ValueError:
            try:
                # Assume the date-string is a date, not an offset
                parsed_dates.append(
                    dateutil.parser.parse(date_string, fuzzy=True)
                )
            except ValueError:
                # The date given was not valid!
                print("%s is not a valid date!" % date_string, file=sys.stderr)

    return parsed_dates


def write_timestamp(entry_path, this_datetime=datetime.datetime.today()):
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
        entry_path: A string containing a path to a journal entry,
            already created or not.
        this_datetime: An optional datetime.datetime object representing
            today's date.
    """
    # Get strings for today's date and time
    this_date = this_datetime.strftime("%Y-%m-%d")
    this_time = this_datetime.strftime("%H:%M")

    # Check if journal entry already exists. If so write, the date and
    # time to it.
    if not os.path.isfile(entry_path):
        with open(entry_path, "x") as jrnl_entry:
            jrnl_entry.write(this_date + "\n" + this_time + "\n")
    else:
        # Find if date already written
        entry_text = open(entry_path).read()

        if this_date in entry_text:
            print_date = False
        else:
            print_date = True

        # Find if we need to insert a newline at the bottom of the file
        if entry_text.endswith("\n\n"):
            print_newline = False
        else:
            print_newline = True

        # Write to the file
        with open(entry_path, "a") as jrnl_entry:
            jrnl_entry.write(
                print_newline * "\n"
                + (this_date + "\n") * print_date
                + this_time
                + "\n\n"
            )


def open_entry(
    datetime_obj,
    editor,
    journal_path,
    do_timestamp,
    in_read_mode,
    error_stream=sys.stderr,
):
    """Try opening a journal entry.

    Args:
        datetime_obj: A datetime.datetime object containing which day's
            journal entry to open.
        editor: A string containing the name of the editor to use.
        journal_path: A string containing the path to the journal's base
            directory.
        do_timestamp: A boolean signalling whether to append a timestamp
            to a journal entry before opening.
        in_read_mode: A boolean signalling whether to only open existing
            entries ("read mode").
        error_stream: An optional TextIO object to send error messages
            to. Almost certainly you want to use the default standard error
            output.
    """

    # Determine path the journal entry text file
    year_dir_path = os.path.join(journal_path, str(datetime_obj.year))
    entry_path = os.path.join(
        year_dir_path, datetime_obj.strftime("%Y-%m-%d") + ".txt"
    )

    # If in read mode, only open existing entries
    if in_read_mode and not os.path.exists(entry_path):
        print("%s does not exist!" % entry_path, file=error_stream)
        return

    # Make the year directory if necessary
    if not os.path.isdir(year_dir_path):
        os.makedirs(year_dir_path)

    # Append timestamp to journal entry if necessary
    if do_timestamp:
        write_timestamp(entry_path)

    # Open the date's journal
    subprocess.Popen([editor, entry_path]).wait()
