# jrnl

A program to help manage a personal journal.

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

You can open up additional dates' journals by specifying addional
positional arguments. One way of doing this is with negative date
offsets.  For example, to open up yesterday's journal run

```
jrnl -1
```

### Fuzzy dates

If you're specifying dates the usual way, jrnl uses
[dateutil](https://github.com/dateutil/dateutil/)'s fuzzy date parser to
parse the dates you pass in. This lets you specify dates like

```
jrnl "Nov 7 2017"
```

dateutil can do much more, for example, specifying the 4th of the
current month's date with

```
jrnl 4
```

### Extending a date past midnight

When it's 02:00, we're likely to refer this time as night, rather than
morning. Likewise, you might want a journal entry written at 02:00 to be
in the same file as entries from (technically) the previous day. If you
do want such a thing, you can specify how many hours past midnight you
want to be considered as part of the previous day's journal file in the
config settings.

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
pip3 install jrnl-mw
```

Run the above as root to get a nice `man` page with the program.
