"""Contains a few helper functions."""

import distutils.util
import os
import subprocess
import sys


def getUserEditor():
    """Return a string containing user's favourite editor."""
    # Try finding editor through environment variable lookup
    editorName = os.environ.get("EDITOR")

    if editorName:
        return editorName

    # Leave it to the user
    return "editor_name_here"


def isProgramAvailable(programName):
    """Find if program passed in is available.

    There's probably a better way to do this that's portable, and in a
    sense this is not "safe", but for the scope of this program, this
    approach is fine.

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

    Arg:
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
