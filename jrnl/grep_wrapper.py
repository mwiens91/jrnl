"""Grep wrapper for jrnl."""

import subprocess


def grep_wrapper(pattern, journal_root, extra_opts=None):
    """Implements a grep search for jrnl.

    Args:
        pattern: A string containing the grep search pattern.
        journal_root: A string containing the journal root's path.
        extra_ops: An optional list of strings contiaining extra options
            to supply to grep.
    """
    # Make extra options an empty list if they don't exist
    if extra_opts is None:
        extra_opts = []

    # Now grep - recursively and ignoring binary files
    subprocess.Popen(
        ["grep", "-r", "-I"] + extra_opts + [pattern, journal_root]
    ).wait()
