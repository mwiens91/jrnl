# jrnl

A program to help manage a personal journal.

## Usage

Set up your journal by printing out a config file, like so:

```
jrnl --setup
```
and fill out the path to the root of your journal.

Open up today's journal entry with

```
jrnl
```

which will open up the appropriate journal entry in your favourite text editor.

You can generate a timestamp before opening the entry by using the `-t` flag:

```
jrnl -t
```

or you can have timestamps always written by specifying so in the config file.

To open up yesterday's journal, or January 1 1999's journal, type

```
jrnl -1
jrnl "January 1 1999"
```

You can open up more than one date at once by giving more date
arguments.

## Other details

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
