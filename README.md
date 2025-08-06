[![PyPI](https://img.shields.io/pypi/v/jrnl-mw.svg)](https://pypi.org/project/jrnl-mw/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jrnl-mw.svg)](https://pypi.org/project/jrnl-mw/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# jrnl

jrnl is a personal journal management application.

## Usage

### Setup

Set up your journal by printing out a config file, like so:

```
jrnl --setup
```

and fill out the path to the root of your journal.

### Using jrnl

Open up today's journal entry with

```
jrnl
```

which will open up today's journal entry in your favourite text editor.

### Using jrnl grep

jrnl also comes with a grep wrapper which you can invoke as follows:

```
jrnl grep [OPTIONS] PATTERN
```

where `OPTIONS` are normal [grep
options](http://man7.org/linux/man-pages/man1/grep.1.html).

## Advanced usage

### Timestamps

You can generate a timestamp before opening the entry by using the `-t` flag:

```
jrnl -t
```

or you can have timestamps always written by specifying so in your config file.

### Negative date offsets

You can open up another date's journal entry by specifying a date as an
argument. One way of doing this is with negative date offsets: for
example, to open up yesterday's journal run

```
jrnl -1
```

### Fuzzy dates

Another way to pass a date to jrnl is with a date string (wrapped in
quotes if it contains spaces). jrnl uses
[dateutil](https://github.com/dateutil/dateutil/)'s fuzzy date parser to
parse the strings you pass in, which lets you specify dates like ``"Nov
7 2017"``:

```
jrnl "Nov 7 2017"
```

dateutil can do more: for example, specifying the 4th of the current
month's date with

```
jrnl 4
```

### Accessing the latest existing entry

You can open the latest existing journal entry with `HEAD` like so:

```
jrnl HEAD
```

Aliases for `HEAD` are `LAST` and `LATEST`—all of which are case
insensitive.

### Accessing an existing entry's ancestor

You can access the ancestor of an existing entry with suffixes `^` or
`~N` (for the Nth ancestor). These work almost identically to the same
suffixes in `git`. For example, to find the fifth last existing journal
enty, you can do

```
jrnl HEAD~5
```

### Accessing the closest existing entry to a given date

To access the closest existing journal entry for a given date, add the
`@` prefix to the date. For example, to find the closest entry to
2017-01-01, you'd do

```
jrnl @2017-01-01
```

### Opening multiple entries

To open up multiple entries simply pass in multiple date arguments. For
example,

```
jrnl -7 "Jan 01 2016" 20180504
```

will open entries for a week ago, 2018-01-01, and 2018-05-04.

### Extending a date past midnight

If in your config file you have

```yaml
hours_past_midnight_included_in_date: N
```

where `N` is some postive integer; then for a given date, at 0`N`:00 or
earlier, jrnl will open up the day before's journal entry.

:confused: What? Here's the motivation:

When it's 02:00, we're likely to refer to this time as night, rather
than morning. Likewise, you might want a journal chunk (for lack of a
better term) written at 02:00 to be in the same entry as chunks from
(technically) the previous day. If you do want such a thing, you can
specify a time in your config file: at any time before this specified
time (inclusive), jrnl will open up the day before's journal entry.

## Journal structure

Right now you're constrained to having a journal structure like so:

```
journal_root/
journal_root/2017/
journal_root/2017/2017-07-05.txt
journal_root/2017/2017-09-01.txt
```

and if you want to use all the features you're going to need to be okay
with ISO 8601-based timestamps:

```
2017-09-01
21:06

You'd write stuff here.

22:30

And more stuff here.
```

## How do I install this?

```
pipx install jrnl-mw
```

or just run the [`run_jrnl.py`](run_jrnl.py) script directly.
