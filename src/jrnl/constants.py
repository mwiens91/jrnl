"""Contains constants for the program."""


# The options which must be specified in config file
EDITOR = "editor"
JOURNAL_PATH = "journal_path"
HOURS_PAST_MIDNIGHT_INCLUDED_IN_DATE = "hours_past_midnight_included_in_date"
CREATE_NEW_ENTRIES_WHEN_SPECIFYING_DATES = (
    "create_new_entries_when_specifying_dates"
)
WRITE_TIMESTAMPS_BY_DEFAULT = "write_timestamps_by_default"

CONFIG_KEYS = {
    EDITOR,
    JOURNAL_PATH,
    HOURS_PAST_MIDNIGHT_INCLUDED_IN_DATE,
    CREATE_NEW_ENTRIES_WHEN_SPECIFYING_DATES,
    WRITE_TIMESTAMPS_BY_DEFAULT,
}
