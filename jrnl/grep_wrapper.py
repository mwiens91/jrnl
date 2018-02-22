"""Grep wrapper for jrnl."""

import os
import subprocess


def grep_wrapper(pattern, journal_root, years=None, extra_opts=None):
    """Implements a grep search for jrnl.

    Args:
        pattern: A string containing the grep search pattern.
        journal_root: A string containing the journal root's path.
        years: An optional list of strings containing the years whose
            entries will be searched in.
        extra_ops: An optional list of strings contiaining extra options
            to supply to grep.
    """
    # First get the directories we need
    if years:
        search_dirs = []

        for year in years:
            if len(year) == 4 and year.isdigit():
                # Add the year directory if it exists. Otherwise ignore
                # it silently
                yearpath = os.path.join(journal_root, year)

                if os.path.exists(yearpath):
                    search_dirs.append(yearpath)
    else:
        # Search the whole journal
        search_dirs = [journal_root]

    # Make extra options an empty list if they don't exist
    if extra_opts is None:
        extra_opts = []

    # Now grep - recursively and ignoring binary files
    subprocess.Popen(['grep', '-r', '-I']
                     +  extra_opts
                     + [pattern]
                     + search_dirs).wait()
