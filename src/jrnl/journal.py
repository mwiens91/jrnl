"""Contains functions relating to opening journal entries."""

import datetime
from functools import reduce
import operator
import os
import re
import subprocess
import sys
import dateutil.parser
from .helpers import find_closest_date


class EntryNotFoundException(Exception):
    """A general exception used when an entry can't be found."""

    pass


class EntryAncestorNotFoundException(EntryNotFoundException):
    """An exception used when an entry's ancestor can't be found."""

    pass


class EntryArgumentNotFoundException(EntryNotFoundException):
    """An exception used a passed in entry date can't be found."""

    pass


class EntryNeighbourNotFoundException(EntryNotFoundException):
    """An exception used when an entry's neighbour can't be found."""

    pass


class JournalHeadNotFoundException(EntryNotFoundException):
    """An exception used when no journal head can be found."""

    pass


def get_existing_year_directories(journal_path):
    """Get year strings for existing years in journal.

    The years are returned in ascending order.

    Args:
        journal_path: A string containing the path to the journal's base
            directory.

    Returns:
        A list of strings containing years for which there are year
        directories in the journal's base directory.
    """
    return sorted(
        [y for y in os.listdir(journal_path) if re.match(r"\d{4}", y)]
    )


def get_years_existing_entry_dates(year, journal_path):
    """Get dates for all existing journal entries within a given year.

    The dates are returned in ascending order.

    Args:
        year: An string specifying the year to get entries for.
        journal_path: A string containing the path to the journal's base
            directory.

    Returns:
        A list of datetime.dates corresponsing to dates for which there
        are existing entries within the specified year.
    """
    # Get all file names
    year_dir_path = os.path.join(journal_path, year)
    file_names = os.listdir(year_dir_path)

    # Filter for valid dates
    date_strings = [
        d[:-4] for d in file_names if re.match(r"\d{4}-\d{2}-\d{2}.txt", d)
    ]

    # Build date objects for the dates
    dates = [
        datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in date_strings
    ]

    return sorted(dates)


def get_all_entry_dates(journal_path):
    """Get a list of all existing entry dates.

    Sorted in ascending order.

    Args:
        journal_path: A string containing the path to the journal's base
            directory.

    Returns:
        A list of datetime.dates corresponsing to dates for which there
        are existing entries.
    """
    entries_by_year = [
        entry
        for entry in [
            get_years_existing_entry_dates(year, journal_path)
            for year in get_existing_year_directories(journal_path)
        ]
    ]

    # See https://stackoverflow.com/a/45323085 for a comparison of
    # flattening solutions in Python (hint: it's the one I'm using here)
    return reduce(operator.iconcat, entries_by_year, [])


def find_entrys_nth_ancestor(date, n, journal_path):
    """Find a given entry's nth ancestor.

    Ancestors meaning the existing entries preceding the date
    corresponding to an existing entry. n can be any integer: note that
    negative or vanishing n is fine.

    Args:
        date: A datetime.date object corresponding to an existing
            entry's date.
        n: An integer specifying the nth ancestor of the passed.
        journal_path: A string containing the path to the journal's base
            directory.

    Returns:
        A datetime.date corresponding to the nth ancestor of the entry
        given by the passed in date.

    Raises:
        EntryAncestorNotFoundException: The entry's nth ancestor can't
            be found.
        EntryArgumentNotFoundException: The entry corresponding to the
            passed in date doesn't exist.
    """
    # Get all the existing entry dates. This could be optimized to
    # include fewer years, but realistically, it's so fast anyway that I
    # don't care; grabbing all entries greatly simplifies the logic of
    # this function.
    year_entries = get_all_entry_dates(journal_path)

    # Get the index of the target entry
    try:
        target_index = year_entries.index(date)
    except ValueError:
        # Passed in date doesn't have an entry!
        raise EntryArgumentNotFoundException

    # Calculate the ancestor's index and validate
    ancestor_index = target_index - n

    if ancestor_index < 0 or ancestor_index >= len(year_entries):
        raise EntryAncestorNotFoundException

    # Valid. Return the date.
    return year_entries[ancestor_index]


def find_closest_existing_entry(date, journal_path):
    """Find the closest existing entry given a date.

    Args:
        date: A datetime.date object to use to find a closest existing
            entry date.
        journal_path: A string containing the path to the journal's base
            directory.

    Returns:
        A datetime.date corresponding to the closest existing entry to
        the passed in date.

    Raises:
        EntryNeighbourNotFoundException: No existing entry could be
            found.
    """
    # Get all the existing entry dates
    year_entries = get_all_entry_dates(journal_path)

    if not year_entries:
        raise EntryAncestorNotFoundException

    return find_closest_date(year_entries, date)


def find_lastest_existing_entry(journal_path):
    """Find the latest existing journal entry's date.

    Args:
        journal_path: A string containing the path to the journal's base
            directory.

    Returns:
        A datetime.date specifying the date corresponding to the latest
        entry.

    Raises:
        JournalHeadNotFoundException: The latest entry couldn't be found.
    """
    # Iterate through existing years until we find an existing entry
    existing_years = get_existing_year_directories(journal_path)

    for year in existing_years[::-1]:
        year_dates = get_years_existing_entry_dates(year, journal_path)

        if year_dates:
            return year_dates[-1]

    # No journal head found
    raise JournalHeadNotFoundException


def parse_ancestor_offsets(date_arg):
    """Parse any ancestor offsets in date runtime argument.

    The date argument passed in doesn't *need* to have any of these
    offsets.

    Args:
        date_arg: A string containing a date argument to be
            parsed.

    Returns:
        A two-tuple containing the passed in date argument with the
        offest portion removed and an integer N specifying that the date
        argument's offsets have said to use the Nth ancestor of the
        passed in date.
    """
    tilde_pattern = r".*~(-?\d*)$"
    offset = 0

    while True:
        # Test for caret
        if date_arg.endswith("^"):
            offset += 1

            date_arg = date_arg[:-1]

            continue

        # Test for tilde offsetting
        regex_match = re.match(tilde_pattern, date_arg)

        if regex_match and regex_match.group(1):
            offset_str = regex_match.group(1)

            offset += int(offset_str)

            date_arg = date_arg[: -(len(offset_str) + 1)]

            continue

        # No offsets left to parse
        return (date_arg, offset)


def parse_dates(date_args, late_night_date_offset, journal_path):
    """Parse dates given in runtime arguments.

    Args:
        date_args: A list of strings containing date arguments to be
            parsed.
        late_night_date_offset: A datetime.timedelta specifying whether
            to shift the raw date back a day.
        journal_path: A string containing the path to the journal's base
            directory.

    Returns:
        A list of datetime.dates representing the entry dates to open.
    """
    # Parse dates given in runtime argument
    parsed_dates = []

    for date_string in date_args:
        original_date_string = date_string
        parsed_date = None

        # First check of ancestor offseting
        date_string, ancestor_offset = parse_ancestor_offsets(date_string)

        # Then check for prefix @ (find closest date)
        if date_string.startswith("@"):
            # Remove the prefix
            date_string = date_string[1:]

            do_find_closest_entry = True
        else:
            do_find_closest_entry = False

        # Check for journal head
        try:
            assert date_string.lower() in ("head", "last", "latest")

            parsed_date = find_lastest_existing_entry(journal_path)
        except JournalHeadNotFoundException:
            # No journal head!
            print("No existing journal entry found!", file=sys.stderr)

            continue
        except AssertionError:
            pass

        # Check for negative date offsetting
        if parsed_date is None:
            try:
                date_offset = int(date_string)

                if date_offset > 0:
                    # Don't allow date offseting from the future. Check
                    # if the argument passed in is a date instead
                    raise ValueError

                # Create datetime object using date offset from current
                # day
                parsed_date = (
                    datetime.date.today()
                    + datetime.timedelta(days=date_offset)
                    + late_night_date_offset
                )
            except OverflowError:
                print(
                    "%s is too large an offset!" % date_offset, file=sys.stderr
                )

                continue
            except ValueError:
                pass

        # Check if the date-string is a proper date
        if parsed_date is None:
            try:
                parsed_date = dateutil.parser.parse(
                    date_string, fuzzy=True
                ).date()
            except ValueError:
                pass

        # Complain if the date couldn't be parsed
        if parsed_date is None:
            print("%s is not a valid date!" % date_string, file=sys.stderr)

            continue

        # Apply @ matching if it was provided
        if do_find_closest_entry:
            try:
                parsed_date = find_closest_existing_entry(
                    parsed_date, journal_path
                )
            except EntryNeighbourNotFoundException:
                # No existing journal entries!
                print("No existing journal entry found!", file=sys.stderr)

        # Apply ancestor offseting if any was given
        if ancestor_offset:
            try:
                parsed_date = find_entrys_nth_ancestor(
                    parsed_date, ancestor_offset, journal_path
                )
            except EntryArgumentNotFoundException:
                # No entry to base ancestor off of
                print(
                    "Base of %s does not correspond to an existing entry!"
                    % original_date_string,
                    file=sys.stderr,
                )
                print(
                    "Ancestor lookup needs to be based on an existing entry!",
                    file=sys.stderr,
                )

                continue
            except EntryAncestorNotFoundException:
                # Ancestor does not exist
                print(
                    "Ancestor %s does not exist!" % original_date_string,
                    file=sys.stderr,
                )

                continue

        # All good!
        parsed_dates.append(parsed_date)

    return parsed_dates


def write_timestamp(entry_path, this_datetime=datetime.datetime.today()):
    """Write timestamp to entry, if one doesn't already exist.

    Modifies a text file to include the passed in datetime's time and
    possibly date in ISO 8601 format. How this works depends on the file
    being created/modified:

    (1) If the entry text file doesn't already exist, create it
        and write the date and time to the top of the file.
    (2) If the entry already exists, look inside and see if
        the datetime's date is already written.  If the datetime's date
        is not written, append the date and time to the file, ensuring
        at least one empty line between the date and time and whatever
        text came before it. If the datetime's date *is* written, follow
        the same steps as but omit writing the date; i.e., write only
        the time.

    Args:
        entry_path: A string containing a path to a entry, already
            created or not.
        this_datetime: An optional datetime.datetime object representing
            the time to write a timestamp for.
    """
    # Get strings for today's date and time
    this_date = this_datetime.strftime("%Y-%m-%d")
    this_time = this_datetime.strftime("%H:%M")

    # Check if entry already exists. If so write, the date and time to
    # it.
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
    date,
    editor,
    journal_path,
    do_timestamp,
    in_read_mode,
    error_stream=sys.stderr,
):
    """Try opening a journal entry.

    Args:
        date: A datetime.date object containing which day's journal
            entry to open.
        editor: A string containing the name of the editor to use.
        journal_path: A string containing the path to the journal's base
            directory.
        do_timestamp: A boolean signalling whether to append a timestamp
            to a entry before opening.
        in_read_mode: A boolean signalling whether to only open existing
            entries ("read mode").
        error_stream: An optional TextIO object to send error messages
            to. Almost certainly you want to use the default standard error
            output.
    """
    # Determine path the entry text file
    year_dir_path = os.path.join(journal_path, str(date.year))
    entry_path = os.path.join(
        year_dir_path, date.strftime("%Y-%m-%d") + ".txt"
    )

    # If in read mode, only open existing entries
    if in_read_mode and not os.path.exists(entry_path):
        print("%s does not exist!" % entry_path, file=error_stream)
        return

    # Make the year directory if necessary
    if not os.path.isdir(year_dir_path):
        os.makedirs(year_dir_path)

    # Append *right now*'s timestamp to entry if specified
    if do_timestamp:
        write_timestamp(entry_path)

    # Open the date's entry
    subprocess.Popen([editor, entry_path]).wait()
