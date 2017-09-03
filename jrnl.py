#!/usr/bin/env python3
# coding: utf-8
"""Code description."""

NAME = "jrnl"
VERSION = "0.0.0"
DESCRIPTION = "%(prog)s - GREAT PROGRAM A+"

import argparse


def main():
    # Parse runtime options
    parseRuntimeArguments()


def parseRuntimeArguments():
    """Parse runtime arguments using argparse.

    This will henerally return arguments as attributes, though some
    arguments will cause the program to exit.

    Returns:
        An object of type 'argparse.Namespace' containing the runtime
        arguments as attributes. See argparse documentation for more
        details.
    """
    parser = argparse.ArgumentParser(
            prog=NAME,
            description=DESCRIPTION,)

    parser.add_argument(
            "--setup",
            help="print jnrl configuration file and exit",
            action=PringConfigAction)
    parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s" + VERSION)

    return parser.parse_args()


class PrintConfigAction(argparse.Action):
    """argparse action to print configuration file."""
    def __init__(self, option_strings, *args, **kwargs):
        super(ConfigPrintAction, self).__init__(option_strings, *args, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        # Commands to dump config file here


if __name__ == '__main__':
    # Run from command line
    main()
