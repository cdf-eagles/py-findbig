#!/usr/bin/env python3
#
# https://github.com/cdf-eagles/py-findbig
#
# A Python implementation of Jason Fesler's (https://github.com/jfesler) Perl
# "findbig" script.
#
"""
Find the largest files and directories in the current (or specified)
directory and list them largest to smallest, as a table, as
comma-separated values, or as JSON
"""

import argparse
import csv
import heapq
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from operator import itemgetter

# The release this script belongs to, as tagged on GitHub without the "v"
__version__ = "0.5.0"
NAME_MIN_WIDTH = 16
AGE_WIDTH = 12
SIZE_WIDTH = 10
# Every column but the name, the three " | " separators, and one spare column
FIXED_WIDTH = 2 * AGE_WIDTH + SIZE_WIDTH + 3 * 3 + 1
SIZE_UNITS = ("K", "M", "G", "T")
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
YEAR = 365 * DAY


def human_size(size):
    """
    Return a size in bytes as text: bytes below 1024, otherwise the largest
    unit up to terabytes that keeps the value, rounded to two places, below
    1024.
    """
    if size < 1024:
        return f"{size}B"
    value = float(size)
    for unit in SIZE_UNITS:
        value /= 1024
        if round(value, 2) < 1024:
            return f"{round(value, 2)}{unit}"
    return f"{round(value, 2)}{SIZE_UNITS[-1]}"


def format_age(seconds):
    """Return an age in seconds in the largest unit up to years."""
    if seconds <= MINUTE:
        return f"{seconds:.2f} (sec)"
    for limit, unit_seconds, unit in (
        (HOUR, MINUTE, "min"),
        (DAY, HOUR, "hr"),
        (YEAR, DAY, "d"),
    ):
        if seconds < limit:
            return f"{seconds / unit_seconds:.2f} ({unit})"
    return f"{seconds / YEAR:.2f} (yr)"


def creation_column(stat_type=os.stat_result):
    """
    Return the creation column's label and the stat field it reads: the birth
    time where the operating system records one, otherwise the inode change
    time.
    """
    if hasattr(stat_type, "st_birthtime"):
        return "Created", "st_birthtime"
    return "Changed", "st_ctime"


def ages(path, field, now):
    """
    Return the ages of path from field and from its modification time, read
    from the entry itself with one lstat; "-" when it cannot be read or the
    time is not recorded.
    """
    try:
        info = os.lstat(path)
    except OSError:
        return "-", "-"
    created = getattr(info, field)
    created_age = format_age(now - created) if created > 0 else "-"
    return created_age, format_age(now - info.st_mtime)


def entry_size(entry):
    """
    Return a file entry's size in bytes: 0 for a symbolic link or an entry
    that can no longer be read.
    """
    try:
        if entry.is_symlink():
            return 0
        return entry.stat(follow_symlinks=False).st_size
    except OSError:
        return 0


def is_directory(entry):
    """Return True if entry is a directory and not a symbolic link."""
    try:
        return entry.is_dir(follow_symlinks=False)
    except OSError:
        return False


def walk_sizes(top):
    """
    Return the size in bytes of top and of every file and directory under it.
    A directory's size is the total of the files below it. Symbolic links
    count as 0 bytes and are not followed, and an entry that vanishes or
    cannot be read counts as 0 bytes.
    """
    sizes = {}
    subdirectories = {}
    pending = [top]
    while pending:
        path = pending.pop()
        # Placed before its entries so a directory sorts ahead of a tie
        sizes[path] = 0
        found = []
        total = 0
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if is_directory(entry):
                        found.append(entry.path)
                    else:
                        size = entry_size(entry)
                        sizes[entry.path] = size
                        total += size
        except OSError:
            pass
        sizes[path] = total
        subdirectories[path] = found
        pending.extend(reversed(found))

    # A directory is listed before everything under it, so reversed order
    # totals every subdirectory before its parent.
    for path in reversed(list(subdirectories)):
        sizes[path] += sum(sizes[sub] for sub in subdirectories[path])
    return sizes


def largest(sizes, count):
    """Return the count largest (path, size) pairs, largest first."""
    return heapq.nlargest(count, sizes.items(), key=itemgetter(1))


def print_table(rows):
    """Print (path, size) rows as a table sized for the terminal."""
    label, field = creation_column()
    columns = shutil.get_terminal_size().columns
    longest = max(len(path) for path, _ in rows)
    width = max(NAME_MIN_WIDTH, min(longest, columns - FIXED_WIDTH))

    header = (
        f"{'Directory/File':^{width}} | {label:^{AGE_WIDTH}} | "
        f"{'Modified':^{AGE_WIDTH}} | {'Size':^{SIZE_WIDTH}}"
    )
    print(header.rstrip())
    print(
        "-|-".join("-" * w for w in (width, AGE_WIDTH, AGE_WIDTH, SIZE_WIDTH))
    )

    now = time.time()
    for path, size in rows:
        created, modified = ages(path, field, now)
        print(
            f"{path[:width]:<{width}} | {created:<{AGE_WIDTH}} | "
            f"{modified:<{AGE_WIDTH}} | {human_size(size):>{SIZE_WIDTH}}"
        )


def utc_timestamp(seconds):
    """Return a time in seconds since the epoch as ISO 8601 text in UTC."""
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat(
        timespec="seconds"
    )


def utc_times(path, field):
    """
    Return the times of path from field and from its modification time as
    UTC timestamps, read from the entry itself with one lstat; None when it
    cannot be read or the time is not recorded.
    """
    try:
        info = os.lstat(path)
    except OSError:
        return None, None
    created = getattr(info, field)
    created_time = utc_timestamp(created) if created > 0 else None
    return created_time, utc_timestamp(info.st_mtime)


def times(path, field):
    """
    Return the times of path from field and from its modification time as
    UTC timestamps; empty when it cannot be read or the time is not recorded.
    """
    return tuple(value or "" for value in utc_times(path, field))


def write_csv(rows, stream=None):
    """
    Write (path, size) rows as comma-separated values with a header row:
    the full path, the size in bytes, and the creation (or change) and
    modification times in UTC.
    """
    label, field = creation_column()
    writer = csv.writer(stream or sys.stdout, lineterminator="\n")
    writer.writerow(("path", "size_bytes", label.lower(), "modified"))
    for path, size in rows:
        writer.writerow((path, size) + times(path, field))


def write_json(rows, stream=None):
    """
    Write (path, size) rows as one JSON array of objects with the same fields
    as the comma-separated values; a time that cannot be read or is not
    recorded is null.
    """
    label, field = creation_column()
    records = []
    for path, size in rows:
        created, modified = utc_times(path, field)
        records.append(
            {
                "path": path,
                "size_bytes": size,
                label.lower(): created,
                "modified": modified,
            }
        )
    stream = stream or sys.stdout
    json.dump(records, stream, indent=2)
    stream.write("\n")


def findbig(search_path, rows_to_print, csv_output=False, json_output=False):
    """
    Walk search_path and print its largest files and directories, as a table,
    as comma-separated values when csv_output is true, or as JSON when
    json_output is true.
    """
    rows = largest(walk_sizes(search_path), rows_to_print)
    if csv_output:
        write_csv(rows)
    elif json_output:
        write_json(rows)
    else:
        print_table(rows)


def existing_directory(path):
    """Return the search path if it names an existing directory"""
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"{path} is not a directory")
    return path


def positive_int(text):
    """Return text as an integer if it is a whole number greater than 0"""
    try:
        value = int(text)
    except ValueError:
        value = 0
    if value <= 0:
        raise argparse.ArgumentTypeError(
            f"{text} is not a whole number greater than 0"
        )
    return value


def build_parser():
    """Return the command line parser"""
    parser = argparse.ArgumentParser(
        description="This script recursively finds the largest "
        "files/directories in the current working directory (default) or "
        "the specified directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Example: %(prog)s -n 10 /tmp",
    )
    parser.add_argument(
        "search_path",
        nargs="?",
        default="./",
        type=existing_directory,
        help="If provided, program will search the provided path instead of "
        "the current working directory.",
    )
    parser.add_argument(
        "-n",
        "--num",
        dest="lines_to_print",
        metavar="LINES",
        type=positive_int,
        default=max(1, shutil.get_terminal_size().lines - 5),
        help="The number of lines to display.",
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument(
        "--csv",
        dest="csv_output",
        action="store_true",
        help="Write comma-separated values (path, size in bytes, and UTC "
        "times) instead of the table.",
    )
    output.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Write a JSON array of objects (path, size in bytes, and UTC "
        "times) instead of the table.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s v{__version__}",
        help=f"Show the release version (v{__version__}) and exit.",
    )
    return parser


def parse_args(argv=None):
    """Return the parsed command line arguments"""
    return build_parser().parse_args(argv)


def main(argv=None):
    """main function execution"""
    args = parse_args(argv)
    findbig(
        args.search_path,
        args.lines_to_print,
        args.csv_output,
        args.json_output,
    )


if __name__ == "__main__":
    main()
