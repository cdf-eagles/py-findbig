[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![CI](https://github.com/cdf-eagles/py-findbig/actions/workflows/ci.yaml/badge.svg)](https://github.com/cdf-eagles/py-findbig/actions/workflows/ci.yaml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=bugs)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![main](https://img.shields.io/badge/main-stable-green.svg?maxAge=2592000)](https://github.com/cdf-eagles/py-findbig/tree/main)

# Python Implementation of 'findbig'

This is a Python 3 implementation of [Jason Fesler's](https://github.com/jfesler) Perl 5 'findbig' script. It lists the largest files and directories under the current directory, or a directory you name, largest first.

It has been tested on macOS and FreeBSD, and it should work on other UNIX and Linux systems with Python 3 installed. It needs only the Python standard library.

## Installation

Clone the repository and link the script into a directory on your `PATH`:

```
git clone https://github.com/cdf-eagles/py-findbig.git
ln -s "$PWD/py-findbig/findbig.py" ~/bin/findbig.py
```

## What it reports

* Each row is a file or directory under the search path, largest first, up to the number of lines asked for. Of two entries the same size, a directory is listed before what is in it.
* A directory's size is the total of the files below it; the size the file system reports for the directory itself is not counted, so an empty directory shows `0B`. A hard-linked file counts once for each of its names.
* Sizes are apparent sizes (the bytes in each file), shown in bytes, then kilobytes (K), megabytes (M), gigabytes (G), or terabytes (T) of 1024 each. They are not what `du` shows: `du` counts disk blocks by default, and counts each directory's own size and each hard-linked file once.
* Symbolic links are listed but not followed, and count as 0 bytes. The search path itself may be a symbolic link to a directory.
* A file or directory that vanishes during the walk, or a directory that cannot be read, counts as 0 bytes, and an age that cannot be read shows as `-`.
* The second column is the time since the entry was created, labelled `Created`, on systems that record a birth time, such as macOS and FreeBSD; a file system that records none shows `-`. Elsewhere, such as on Linux, it is the time since the entry's inode last changed, labelled `Changed`.
* Ages are read from each entry itself, so a symbolic link shows its own ages, not its target's.

## Example Usage

### Help

The default number of lines is the terminal's height less 5: a standard 80x24 terminal prints 19 lines. `-n` takes a whole number greater than 0; anything else is a usage error.

```
$ findbig.py -h
usage: findbig.py [-h] [-n LINES] [search_path]

This script recursively finds the largest files/directories in the current
working directory (default) or the specified directory.

positional arguments:
  search_path      If provided, program will search the provided path instead
                   of the current working directory. (default: ./)

options:
  -h, --help       show this help message and exit
  -n, --num LINES  The number of lines to display. (default: 19)

Example: findbig.py -n 10 /tmp
```

The examples below ran on macOS in a newly created tree.

### Default use and output

```
$ findbig.py
 Directory/File  |   Created    |   Modified   |    Size
-----------------|--------------|--------------|-----------
./               | 0.03 (sec)   | 0.03 (sec)   |     160.0M
./a              | 0.03 (sec)   | 0.03 (sec)   |      94.0M
./a/1            | 0.03 (sec)   | 0.03 (sec)   |      84.0M
./b              | 0.03 (sec)   | 0.03 (sec)   |      56.0M
./a/1/file1      | 0.03 (sec)   | 0.03 (sec)   |      52.0M
./b/2            | 0.03 (sec)   | 0.03 (sec)   |      46.0M
./b/2/file2      | 0.03 (sec)   | 0.03 (sec)   |      43.0M
./a/1/z          | 0.03 (sec)   | 0.03 (sec)   |      32.0M
./a/1/z/filez    | 0.03 (sec)   | 0.03 (sec)   |      32.0M
./a/filea        | 0.03 (sec)   | 0.03 (sec)   |      10.0M
./c              | 0.03 (sec)   | 0.03 (sec)   |      10.0M
./c/filec        | 0.03 (sec)   | 0.03 (sec)   |      10.0M
./b/fileb        | 0.03 (sec)   | 0.03 (sec)   |      10.0M
./b/2/y          | 0.03 (sec)   | 0.03 (sec)   |       3.0M
./b/2/y/filey    | 0.03 (sec)   | 0.03 (sec)   |       3.0M
./c/3            | 0.03 (sec)   | 0.03 (sec)   |         0B
./c/3/x          | 0.03 (sec)   | 0.03 (sec)   |         0B
```

### Limit number of lines of output

```
$ findbig.py -n 4
 Directory/File  |   Created    |   Modified   |    Size
-----------------|--------------|--------------|-----------
./               | 0.06 (sec)   | 0.06 (sec)   |     160.0M
./a              | 0.06 (sec)   | 0.06 (sec)   |      94.0M
./a/1            | 0.06 (sec)   | 0.06 (sec)   |      84.0M
./b              | 0.06 (sec)   | 0.06 (sec)   |      56.0M
```

### Limit number of lines of output and specify directory to evaluate

```
$ findbig.py -n 4 ./a
 Directory/File  |   Created    |   Modified   |    Size
-----------------|--------------|--------------|-----------
./a              | 0.09 (sec)   | 0.09 (sec)   |      94.0M
./a/1            | 0.09 (sec)   | 0.09 (sec)   |      84.0M
./a/1/file1      | 0.09 (sec)   | 0.09 (sec)   |      52.0M
./a/1/z          | 0.09 (sec)   | 0.09 (sec)   |      32.0M
```

## Development and CI

See [CONTRIBUTING.md](CONTRIBUTING.md) to set up the checks locally.

The `CI` workflow (`.github/workflows/ci.yaml`) runs on every pull request to `main`, every push to `main`, and weekly. It has these jobs:

* `Lint` runs yamllint, then every pre-commit hook over all files: black, isort, flake8, pylint, actionlint, the GitHub workflow and Dependabot schema checks, and the private-key checks.
* `Secret scan` runs gitleaks over the full git history.
* `Test` runs the unit tests in `tests/` with `python3 -m unittest`.
* `Tool drift` runs weekly and opens an issue when a pinned tool has a newer release.

The tests need only the Python standard library: `python3 -m unittest discover -s tests -t .` runs them locally.

Tool versions live in one place each: Python tools in `ci/requirements.txt`, pre-commit hooks in `.pre-commit-config.yaml`, and the gitleaks release in the workflow `env:` block with its SHA-256 checksum. Dependabot updates all of them.
