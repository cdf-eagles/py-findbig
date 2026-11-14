"""Unit tests for findbig.py, run with python3 -m unittest."""

import argparse
import contextlib
import csv
import io
import os
import shutil
import tempfile
import time
import types
import unittest
from datetime import datetime, timezone
from unittest import mock

import findbig

WIDE_TERMINAL = os.terminal_size((300, 24))


def run_findbig(path, rows=10):
    """Run findbig() on path and return what it printed."""
    out = io.StringIO()
    with mock.patch.object(
        shutil, "get_terminal_size", return_value=WIDE_TERMINAL
    ), contextlib.redirect_stdout(out):
        findbig.findbig(path, rows)
    return out.getvalue()


def run_main(argv):
    """Run main() with argv; return its exit code, stdout, and stderr."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with mock.patch.object(
        shutil, "get_terminal_size", return_value=WIDE_TERMINAL
    ), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            findbig.main(argv)
        except SystemExit as raised:
            code = raised.code
    return code, out.getvalue(), err.getvalue()


def line_for(output, path):
    """Return the table line that starts with path."""
    for line in output.splitlines():
        if line.startswith(path + " "):
            return line
    raise AssertionError(f"no line for {path} in:\n{output}")


def table_paths(output):
    """Return the paths of a table's rows, in order."""
    return [line.split(" | ")[0].rstrip() for line in output.splitlines()[2:]]


def write_file(path, size):
    """Create a file of size bytes."""
    with open(path, "wb") as handle:
        handle.write(b"\0" * size)


class TestFormatting(unittest.TestCase):
    """Size and age formatting."""

    def test_human_readable_units(self):
        """Sizes use bytes, then the largest unit up to terabytes."""
        cases = [
            (0, "0B"),
            (512, "512B"),
            (1023, "1023B"),
            (1536, "1.5K"),
            (3 * 1024**2, "3.0M"),
            (1024**2 - 1, "1.0M"),
            (5 * 1024**3, "5.0G"),
            (7 * 1024**4, "7.0T"),
            (2048 * 1024**4, "2048.0T"),
        ]
        for size, expected in cases:
            self.assertEqual(findbig.human_size(size), expected)

    def test_age_buckets(self):
        """Ages use seconds, minutes, hours, days, and years."""
        cases = [
            (30, "30.00 (sec)"),
            (60, "60.00 (sec)"),
            (120, "2.00 (min)"),
            (7200, "2.00 (hr)"),
            (2 * 86400, "2.00 (d)"),
            (730 * 86400, "2.00 (yr)"),
        ]
        for seconds, expected in cases:
            self.assertEqual(findbig.format_age(seconds), expected)


class TestArguments(unittest.TestCase):
    """The command line arguments."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_directory_is_accepted(self):
        """An existing directory is returned unchanged."""
        self.assertEqual(findbig.existing_directory(self.tmp), self.tmp)

    def test_missing_path_is_refused(self):
        """A path that does not exist is refused."""
        with self.assertRaises(argparse.ArgumentTypeError):
            findbig.existing_directory(os.path.join(self.tmp, "missing"))

    def test_file_is_refused(self):
        """A path that names a file is refused."""
        path = os.path.join(self.tmp, "file")
        write_file(path, 1)
        with self.assertRaises(argparse.ArgumentTypeError):
            findbig.existing_directory(path)

    def test_main_exits_2_on_a_missing_path(self):
        """main() prints the usage error and exits with status 2."""
        code, _, err = run_main([os.path.join(self.tmp, "missing")])
        self.assertEqual(code, 2)
        self.assertIn("is not a directory", err)

    def test_positive_counts_are_accepted(self):
        """A whole number greater than 0 is returned as an integer."""
        self.assertEqual(findbig.positive_int("3"), 3)

    def test_other_counts_are_refused(self):
        """Zero, negative, and non-integer counts are refused."""
        for text in ("0", "-2", "ten", "1.5", ""):
            with self.assertRaises(argparse.ArgumentTypeError):
                findbig.positive_int(text)

    def test_main_exits_2_on_zero_lines(self):
        """-n 0 is a usage error with status 2, not a traceback."""
        code, out, err = run_main(["-n", "0", self.tmp])
        self.assertEqual(code, 2)
        self.assertIn("greater than 0", err)
        self.assertNotIn("Traceback", err)
        self.assertEqual(out, "")

    def test_lines_limit_the_rows(self):
        """-n limits the table to that many rows."""
        for name in ("a", "b", "c"):
            write_file(os.path.join(self.tmp, name), 10)
        code, out, _ = run_main(["-n", "2", self.tmp])
        self.assertEqual(code, 0)
        self.assertEqual(len(table_paths(out)), 2)

    def test_default_lines_follow_the_terminal(self):
        """The default is the terminal's height less 5, and at least 1."""
        for lines, expected in ((24, 19), (3, 1)):
            size = os.terminal_size((80, lines))
            with mock.patch.object(
                shutil, "get_terminal_size", return_value=size
            ):
                args = findbig.parse_args([self.tmp])
            self.assertEqual(args.lines_to_print, expected)


class TestCreationColumn(unittest.TestCase):
    """The creation column's label and source."""

    def test_birth_time_where_recorded(self):
        """A stat result with a birth time gives a Created column."""
        with_birth = types.SimpleNamespace(st_birthtime=None)
        self.assertEqual(
            findbig.creation_column(with_birth), ("Created", "st_birthtime")
        )

    def test_change_time_otherwise(self):
        """A stat result without a birth time gives a Changed column."""
        self.assertEqual(
            findbig.creation_column(types.SimpleNamespace()),
            ("Changed", "st_ctime"),
        )

    def test_unrecorded_birth_time_shows_a_dash(self):
        """A birth time of 0 or less shows as -."""
        now = time.time()
        info = types.SimpleNamespace(st_birthtime=-1, st_mtime=now - 120)
        with mock.patch.object(findbig.os, "lstat", return_value=info):
            self.assertEqual(
                findbig.ages("x", "st_birthtime", now), ("-", "2.00 (min)")
            )

    def test_header_names_the_column(self):
        """The table header uses this system's creation column label."""
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        header = run_findbig(tmp).splitlines()[0]
        self.assertIn(f" {findbig.creation_column()[0]} ", header)


class TestWalk(unittest.TestCase):
    """Walking a tree and printing the largest entries."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.top = os.path.join(self.tmp, "top")
        self.sub = os.path.join(self.top, "sub")
        os.makedirs(self.sub)
        self.big = os.path.join(self.sub, "big.bin")
        write_file(self.big, 2048)

    def test_file_size_is_listed(self):
        """A file is listed with its size."""
        output = run_findbig(self.top)
        self.assertTrue(line_for(output, self.big).endswith("2.0K"))

    def test_directory_size_is_the_total_of_its_files(self):
        """A directory's own size is not added to its total."""
        write_file(os.path.join(self.top, "small.bin"), 100)
        empty = os.path.join(self.top, "empty")
        os.makedirs(empty)
        sizes = findbig.walk_sizes(self.top)
        self.assertEqual(sizes[self.top], 2148)
        self.assertEqual(sizes[self.sub], 2048)
        self.assertEqual(sizes[empty], 0)

    def test_largest_first_and_directory_before_a_tie(self):
        """Rows run largest first; a directory precedes an equal entry."""
        small = os.path.join(self.top, "small.bin")
        write_file(small, 100)
        empty = os.path.join(self.top, "empty")
        os.makedirs(empty)
        self.assertEqual(
            table_paths(run_findbig(self.top)),
            [self.top, self.sub, self.big, small, empty],
        )

    def test_no_line_ends_in_a_space(self):
        """Every table line, the header included, ends without a space."""
        for line in run_findbig(self.top).splitlines():
            self.assertEqual(line, line.rstrip())

    def test_symbolic_link_counts_as_zero(self):
        """A link to a file counts as 0 bytes and is not followed."""
        link = os.path.join(self.top, "link.bin")
        os.symlink(self.big, link)
        sizes = findbig.walk_sizes(self.top)
        self.assertEqual(sizes[link], 0)
        self.assertEqual(sizes[self.top], 2048)

    def test_link_to_a_directory_is_not_followed(self):
        """A link to a directory counts as 0 bytes and is not walked."""
        link = os.path.join(self.top, "loop")
        os.symlink(self.top, link)
        sizes = findbig.walk_sizes(self.top)
        self.assertEqual(sizes[link], 0)
        self.assertNotIn(os.path.join(link, "sub"), sizes)

    @unittest.skipIf(os.geteuid() == 0, "root can read every directory")
    def test_unreadable_directory_is_skipped(self):
        """A subdirectory that cannot be read does not stop the walk."""
        locked = os.path.join(self.top, "locked")
        os.makedirs(os.path.join(locked, "inner"))
        os.chmod(locked, 0)
        self.addCleanup(os.chmod, locked, 0o755)
        output = run_findbig(self.top)
        self.assertTrue(line_for(output, self.big).endswith("2.0K"))
        self.assertTrue(line_for(output, locked).endswith("0B"))

    def test_symbolic_link_search_path(self):
        """A search path that is a link to a directory of files is walked."""
        link = os.path.join(self.tmp, "link")
        os.symlink(self.sub, link)
        output = run_findbig(link)
        big = os.path.join(link, "big.bin")
        self.assertTrue(line_for(output, big).endswith("2.0K"))

    def test_broken_symbolic_link_is_listed(self):
        """A link whose target is gone is listed with its own age."""
        link = os.path.join(self.top, "dangling.sh")
        os.symlink(os.path.join(self.tmp, "missing-target"), link)
        output = run_findbig(self.top)
        line = line_for(output, link)
        self.assertTrue(line.endswith("0B"))
        self.assertNotIn(" - ", line)

    def test_entries_that_vanish_during_the_walk(self):
        """A file and a directory removed once listed count as 0 bytes."""
        gone_dir = os.path.join(self.top, "gone-dir")
        gone_file = os.path.join(self.top, "gone-file")
        os.makedirs(gone_dir)
        write_file(gone_file, 4096)
        real_scandir = os.scandir

        def remove_gone(entries):
            for entry in entries:
                if entry.path == gone_file:
                    os.remove(gone_file)
                elif entry.path == gone_dir:
                    os.rmdir(gone_dir)
                yield entry

        @contextlib.contextmanager
        def scandir(path):
            with real_scandir(path) as entries:
                yield remove_gone(entries)

        with mock.patch.object(findbig.os, "scandir", scandir):
            output = run_findbig(self.top)
        gone = line_for(output, gone_file)
        self.assertTrue(gone.endswith("0B"))
        self.assertIn(" - ", gone)
        self.assertTrue(line_for(output, gone_dir).endswith("0B"))
        self.assertTrue(line_for(output, self.top).endswith("2.0K"))


class TestCsvOutput(unittest.TestCase):
    """The --csv option."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.sub = os.path.join(self.tmp, "sub")
        os.makedirs(self.sub)
        self.big = os.path.join(self.sub, "big.bin")
        write_file(self.big, 2048)
        write_file(os.path.join(self.tmp, "small.bin"), 100)

    def csv_rows(self, *args):
        """Run main() with --csv and args; return the parsed rows."""
        code, out, err = run_main(["--csv", *args])
        self.assertEqual((code, err), (0, ""))
        return list(csv.reader(io.StringIO(out, newline="")))

    def test_off_by_default(self):
        """Without --csv the option is off and the table is printed."""
        self.assertFalse(findbig.parse_args([self.tmp]).csv_output)
        self.assertTrue(findbig.parse_args(["--csv", self.tmp]).csv_output)
        code, out, _ = run_main([self.tmp])
        self.assertEqual(code, 0)
        self.assertTrue(out.splitlines()[0].strip().startswith("Directory"))
        self.assertEqual(table_paths(out)[0], self.tmp)

    def test_header_names_the_columns(self):
        """The header names the path, bytes, creation, and modified."""
        label = findbig.creation_column()[0].lower()
        self.assertEqual(
            self.csv_rows(self.tmp)[0],
            ["path", "size_bytes", label, "modified"],
        )

    def test_rows_read_back_to_the_walk(self):
        """Paths and whole-byte sizes match the walk, largest first."""
        expected = findbig.largest(findbig.walk_sizes(self.tmp), 10)
        rows = self.csv_rows("-n", "10", self.tmp)[1:]
        self.assertEqual([(row[0], int(row[1])) for row in rows], expected)

    def test_lines_limit_the_rows(self):
        """-n limits the rows after the header."""
        self.assertEqual(len(self.csv_rows("-n", "2", self.tmp)), 3)

    def test_awkward_paths_are_quoted(self):
        """A comma, a quote, or a line break in a path survives a read."""
        name = os.path.join(self.tmp, 'odd, "name"\nhere')
        write_file(name, 4096)
        paths = [row[0] for row in self.csv_rows(self.tmp)[1:]]
        self.assertIn(name, paths)

    def test_long_paths_are_not_cut(self):
        """A path wider than the terminal is written whole."""
        deep = os.path.join(self.tmp, "d" * 120, "e" * 120)
        os.makedirs(deep)
        write_file(os.path.join(deep, "f"), 8192)
        narrow = os.terminal_size((80, 24))
        out = io.StringIO()
        with mock.patch.object(
            shutil, "get_terminal_size", return_value=narrow
        ), contextlib.redirect_stdout(out):
            findbig.main(["--csv", self.tmp])
        paths = [row[0] for row in csv.reader(io.StringIO(out.getvalue()))]
        self.assertIn(os.path.join(deep, "f"), paths)

    def test_times_are_utc_timestamps(self):
        """The modified column is the file's mtime in UTC, to the second."""
        os.utime(self.big, (1_700_000_000.75, 1_700_000_000.75))
        row = next(
            row for row in self.csv_rows(self.tmp) if row[0] == self.big
        )
        modified = datetime.fromisoformat(row[3])
        self.assertEqual(modified.utcoffset().total_seconds(), 0)
        self.assertEqual(
            modified,
            datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc),
        )
        self.assertNotEqual(row[2], "")

    def test_unrecorded_or_unreadable_times_are_empty(self):
        """A birth time of 0 or an entry lstat cannot read gives empty."""
        info = types.SimpleNamespace(st_birthtime=0, st_mtime=86400)
        with mock.patch.object(findbig.os, "lstat", return_value=info):
            self.assertEqual(
                findbig.times("x", "st_birthtime"),
                ("", "1970-01-02T00:00:00+00:00"),
            )
        with mock.patch.object(
            findbig.os, "lstat", side_effect=FileNotFoundError
        ):
            self.assertEqual(findbig.times("x", "st_ctime"), ("", ""))


class TestVersion(unittest.TestCase):
    """The release version in --version and --help."""

    def test_version_option_prints_the_release(self):
        """--version prints the release tag and exits with status 0."""
        code, out, _ = run_main(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(out.split()[-1], f"v{findbig.__version__}")

    def test_help_shows_the_release(self):
        """--help names the release version."""
        code, out, _ = run_main(["--help"])
        self.assertEqual(code, 0)
        self.assertIn(f"(v{findbig.__version__})", out)

    def test_version_is_a_release_number(self):
        """The version is three dot-separated numbers, as tags use."""
        self.assertRegex(findbig.__version__, r"^[0-9]+\.[0-9]+\.[0-9]+$")


if __name__ == "__main__":
    unittest.main()
