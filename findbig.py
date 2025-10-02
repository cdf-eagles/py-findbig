#!/usr/bin/env python3
#
# written by Christopher Fernando
# https://github.com/cdf-eagles/py-findbig
#
# This script is an implementation of Jason Fesler's
# (https://github.com/jfesler) Perl "findbig" script that I've found extremely
# useful over the years.
#
"""
Find the largest files in the current (or specified) directory and list them
largest to smallest
"""

import argparse
import datetime
import os
import shutil
import sys
from itertools import islice
from os.path import getsize, join
from pathlib import Path


def take(n, iterable):
    """Return the first n items of the iterable as a list."""
    return list(islice(iterable, n))


def convert_to_human_readable(sorted_list):
    """
    Convert the values of the sorted dictionary from raw bytes to human
    readable up to terabytes. Returns a list with the values in readable
    format.
    """
    converted_list = list(
        map(
            lambda x: (
                (x[0], x[1], "B")
                if x[1] < 1024
                else (
                    (x[0], round(x[1] / 1024, 2), "K")
                    if round(x[1] / 1024, 2) < 1024
                    else (
                        (x[0], round(x[1] / 1024**2, 2), "M")
                        if round(x[1] / 1024**2, 2) < 1024
                        else (
                            (x[0], round(x[1] / 1024**3, 2), "G")
                            if round(x[1] / 1024**3, 2) < 1024
                            else (x[0], round(x[1] / 1024**4, 2), "T")
                        )
                    )
                )
            ),
            sorted_list,
        )
    )
    return converted_list


def calculate_time(time_in_seconds):
    """Convert time_in_seconds to the maximum value of days, months, years."""
    time_string = ""
    t = time_in_seconds.total_seconds()
    if t <= 60:
        time_string = f"{t:.2f} (sec)"
    elif t / 60 < 60:
        time_string = f"{t/60:.2f} (min)"
    elif t / 60**2 < 24:
        time_string = f"{t/60**2:.2f} (hr)"
    elif t / (60 * 60 * 24) < 365:
        time_string = f"{t/(60*60*24):.2f} (d)"
    else:
        time_string = f"{t/(60*60*24*365):.2f} (yr)"

    return time_string


def calculate_age(timestamp):
    """Calculate the age between a timestamp and the current time"""
    current_time = datetime.datetime.now()
    date = datetime.datetime.fromtimestamp(timestamp)
    return calculate_time(current_time - date)


def print_table(sorted_list):
    """Print the results in a human readable table"""
    term_size = shutil.get_terminal_size()
    header = "Directory/File", "Created", "Modified", "Size"
    col1, col2, col3, col4 = 16, 12, 12, 10
    max_length = max(len(x) for x, y, z in sorted_list)

    if col1 < max_length < (int(term_size.columns) - 44):
        col1 = max_length
    else:
        col1 = int(term_size.columns) - 44

    # print header
    print(f"{header[0]:^{col1}} | {header[1]:^{col2}} |", end="")
    print(f"{header[2]:^{col3}} | {header[3]:^{col4}}", end="\n")
    print(f'{"-"*col1:^{col1}}-|-{"-"*col2:^{col2}}-|', end="")
    print(f'-{"-"*col3:^{col3}}-|-{"-"*col4:^{col4}}', end="\n")

    for fobj, size, unit in sorted_list:
        size_unit = str(size) + str(unit)

        # calculate age of filesystem objects in the output list
        age_from_creation = calculate_age(os.path.getctime(fobj))
        age_from_modification = calculate_age(os.path.getmtime(fobj))

        # print data; one line per object
        print(f"{fobj[:col1]:<{col1}} |", end="")
        print(f"{age_from_creation:^{col2}} |", end="")
        print(f"{age_from_modification:^{col3}} |", end="")
        print(f"{size_unit:>{col4}}", end="\n")


def findbig(args_list, rows_to_print):
    """Walk the provided directory and find all the largest files"""
    dirs_dict = {}
    for root, dirs, files in os.walk(args_list.search_path, topdown=False, followlinks=False):  # noqa: E501
        if os.path.islink(root):
            dirs_dict[root] = 0
        else:
            dir_size = getsize(root)

        file_size = 0
        for name in files:
            full_path = join(root, name)
            if os.path.islink(full_path):
                file_size = 0
            else:
                obj = Path(full_path)
                if obj.exists():
                    file_size = getsize(full_path)
            dirs_dict[full_path] = file_size
            dir_size += file_size

        subdir_size = 0
        for d in dirs:
            full_path = join(root, d)
            if os.path.islink(full_path):
                dirs_dict[full_path] = 0
            else:
                obj = Path(full_path)
                if obj.exists():
                    subdir_size += dirs_dict[full_path]

        dirs_dict[root] = dir_size + subdir_size

    sorted_dirs_dict = dict(sorted(dirs_dict.items(), reverse=True, key=lambda item: item[1]))  # noqa: E501
    top_dirs = take(rows_to_print, sorted_dirs_dict.items())

    print_table(convert_to_human_readable(top_dirs))


if __name__ == "__main__":
    terminal_size = shutil.get_terminal_size()

    parser = argparse.ArgumentParser(
        description="This script recursively finds the largest \
                     files/directories in the current working directory \
                     (default) or the specified directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=f"Example: {sys.argv[0]} -n 10 /tmp",
    )

    # optional argument for search path
    parser.add_argument(
        "search_path",
        nargs="?",
        default="./",
        help="If provided, program will search the provided path \
              instead of the current working directory.",
    )

    # optional argument for number of lines to print
    parser.add_argument(
        "-n",
        "--num",
        dest="lines_to_print",
        nargs=1,
        type=int,
        default=terminal_size.lines - 5,
        help="The number of lines to display.",
    )

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        print(f"An error occured: {e}")

    LINES_TO_PRINT = ""
    if args.lines_to_print is not None:
        if isinstance(args.lines_to_print, int):
            LINES_TO_PRINT = args.lines_to_print
        else:
            LINES_TO_PRINT = int("".join(map(str, args.lines_to_print)))

    if LINES_TO_PRINT <= 0:
        raise argparse.ArgumentError(
            LINES_TO_PRINT,
            f"Lines to print must be a value greater than 0: \
              {LINES_TO_PRINT} is not valid",
        )

    try:
        findbig(args, LINES_TO_PRINT)
    except argparse.ArgumentError as e:
        print(f"An error occured: {e}")
        sys.exit(1)

    sys.exit(0)
