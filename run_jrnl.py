#!/usr/bin/env python3
"""Run the jrnl program."""

import os
import sys

# Let me import jrnl
# TODO: Is there a better way to do this without making src a package?
os.chdir(os.path.join(os.getcwd(), "src"))
sys.path.insert(0, "")

from jrnl.main import main

# Run it
main()
