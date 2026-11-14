"""Unit tests for findbig.py, run with python3 -m unittest."""

import argparse
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import findbig

WIDE_TERMINAL = os.terminal_size((300, 24))


def run_findbig(path, rows=10):
    """Run findbig() on path and return what it printed."""
    out = io.StringIO()
    with mock.patch.object(
        shutil, "get_terminal_size", return_value=WIDE_TERMINAL
    ), contextlib.redirect_stdout(out):
        findbig.findbig(argparse.Namespace(search_path=path), rows)
    return out.getvalue()


def line_for(output, path):
    """Return the table line that starts with path."""
    for line in output.splitlines():
        if line.startswith(path + " "):
            return line
    raise AssertionError(f"no line for {path} in:\n{output}")


class TestConversions(unittest.TestCase):
    """Size and age formatting."""

    def test_human_readable_units(self):
        """Sizes use bytes, then kilobytes and megabytes."""
        converted = findbig.convert_to_human_readable(
            [("a", 512), ("b", 2048), ("c", 3 * 1024**2)]
        )
        self.assertEqual(
            converted, [("a", 512, "B"), ("b", 2.0, "K"), ("c", 3.0, "M")]
        )

    def test_time_buckets(self):
        """Ages use seconds, minutes, hours, days, and years."""
        cases = [
            (30, "30.00 (sec)"),
            (120, "2.00 (min)"),
            (7200, "2.00 (hr)"),
            (2 * 86400, "2.00 (d)"),
            (730 * 86400, "2.00 (yr)"),
        ]
        for seconds, expected in cases:
            delta = mock.Mock()
            delta.total_seconds.return_value = seconds
            self.assertEqual(findbig.calculate_time(delta), expected)


class TestSearchPath(unittest.TestCase):
    """The search path argument."""

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
        with open(path, "wb") as handle:
            handle.write(b"x")
        with self.assertRaises(argparse.ArgumentTypeError):
            findbig.existing_directory(path)

    def test_main_exits_2_on_a_missing_path(self):
        """main() prints the usage error and exits with status 2."""
        argv = ["findbig.py", os.path.join(self.tmp, "missing")]
        err = io.StringIO()
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stderr(
            err
        ), self.assertRaises(SystemExit) as raised:
            findbig.main()
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("is not a directory", err.getvalue())


class TestWalk(unittest.TestCase):
    """Walking a tree and printing the largest entries."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.top = os.path.join(self.tmp, "top")
        os.makedirs(os.path.join(self.top, "sub"))
        self.big = os.path.join(self.top, "sub", "big.bin")
        with open(self.big, "wb") as handle:
            handle.write(b"\0" * 2048)

    def test_file_size_is_listed(self):
        """A file is listed with its size."""
        output = run_findbig(self.top)
        self.assertTrue(line_for(output, self.big).endswith("2.0K"))

    @unittest.skipIf(os.geteuid() == 0, "root can read every directory")
    def test_unreadable_directory_is_skipped(self):
        """A subdirectory that cannot be read does not stop the walk."""
        locked = os.path.join(self.top, "locked")
        os.makedirs(os.path.join(locked, "inner"))
        os.chmod(locked, 0)
        self.addCleanup(os.chmod, locked, 0o755)
        output = run_findbig(self.top)
        self.assertTrue(line_for(output, self.big).endswith("2.0K"))

    def test_symbolic_link_search_path(self):
        """A search path that is a link to a directory of files is walked."""
        link = os.path.join(self.tmp, "link")
        os.symlink(os.path.join(self.top, "sub"), link)
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
        """A file and a directory listed but gone count as 0 bytes."""
        real_walk = os.walk

        def walk(path, topdown=True, followlinks=False):
            for root, dirs, files in real_walk(
                path, topdown, followlinks=followlinks
            ):
                if root == self.top:
                    dirs = dirs + ["gone-dir"]
                    files = files + ["gone-file"]
                yield root, dirs, files

        with mock.patch.object(findbig.os, "walk", walk):
            output = run_findbig(self.top)
        gone = line_for(output, os.path.join(self.top, "gone-file"))
        self.assertTrue(gone.endswith("0B"))
        self.assertIn(" - ", gone)
        self.assertTrue(line_for(output, self.big).endswith("2.0K"))


if __name__ == "__main__":
    unittest.main()
