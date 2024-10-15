"""Contains a few helper functions."""

from bisect import bisect_left
from distutils.util import strtobool
import os
import subprocess


def find_closest_date(date_list, target_date):
    """Finds the closest date to a target date.

    This requires the date list to be sorted. If two dates are equally
    close, return the older date.

    Adapted from Lauritz V. Thaulow's post on Stack Overflow here:
    https://stackoverflow.com/a/12141511.

    Args:
        date_list: A sorted list of datetime.dates.
        target_date: A target datetime.date.

    Returns:
        A datetime.date corresponding to the closest date in the date
        list to the target date.
    """
    pos = bisect_left(date_list, target_date)

    if pos == 0:
        return date_list[0]
    if pos == len(date_list):
        return date_list[-1]

    before = date_list[pos - 1]
    after = date_list[pos]

    if after - target_date < target_date - before:
        return after

    return before


def get_user_editor():
    """Return a string containing user's favourite editor."""
    # Try finding editor through environment variable lookup
    editor_name = os.environ.get("EDITOR")

    if editor_name:
        return editor_name

    # Leave it to the user
    return "editor_name_here"


def is_program_available(program_name):
    """Find if program passed in is available.

    There's probably a better way to do this that's portable, and in a
    sense this is not "safe", but for the scope of this program, this
    approach is fine.

    Args:
        program_name: A string containing a program name.

    Returns:
        A boolean specifying whether the program specified is available.
    """
    return not subprocess.Popen(
        ["bash", "-c", "type " + program_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).wait()


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
    print("%s [y/n]: " % query)
    val = input().lower()
    try:
        result = strtobool(val)
    except ValueError:
        # Result no good! Ask again.
        print("Please answer with y/n")
        return prompt(query)
    return result
