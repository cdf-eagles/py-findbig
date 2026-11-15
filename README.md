[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![CI](https://github.com/cdf-eagles/py-findbig/actions/workflows/ci.yaml/badge.svg)](https://github.com/cdf-eagles/py-findbig/actions/workflows/ci.yaml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=bugs)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![main](https://img.shields.io/badge/main-stable-green.svg?maxAge=2592000)](https://github.com/cdf-eagles/py-findbig/tree/main)

# Python Implementation of 'findbig'

This is a Python 3 implementation of [Jason Fesler's](https://github.com/jfesler) Perl 5 'findbig' script. It lists the largest files and directories under the current directory, or a directory you name, largest first, as a table or, with `--csv` or `--json`, as comma-separated values or JavaScript Object Notation (JSON).

It has been tested on macOS and FreeBSD, and it should work on other UNIX and Linux systems with Python 3 installed. It needs only the Python standard library.

## Installation

Each [release](https://github.com/cdf-eagles/py-findbig/releases) from v0.5.0 on publishes packages that install the command as `findbig`, with its manual page (`man findbig`), and depend on the distribution's `python3`. The commands below use v0.5.0's file names; download the files from the release first.

* Debian and Ubuntu: `sudo apt install ./findbig_0.5.0_all.deb`
* Red Hat Enterprise Linux (RHEL), Rocky Linux, AlmaLinux, and Fedora: `sudo dnf install ./findbig-0.5.0-1.noarch.rpm`
* Alpine Linux: the `.apk` is signed, so install its public key first: `sudo cp py-findbig.rsa.pub /etc/apk/keys/`, then `sudo apk add ./findbig_0.5.0_noarch.apk`
* macOS with [Homebrew](https://brew.sh): `brew install cdf-eagles/tap/findbig` installs the command and its manual page from the account's tap ([homebrew-tap](https://github.com/cdf-eagles/homebrew-tap)), with Homebrew's Python, and `brew upgrade findbig` takes each new release; no download is needed.
* FreeBSD 15: `sudo pkg install python3`, then `sudo pkg add ./findbig-0.5.0.pkg`. `pkg add` takes dependencies only from the package's own directory, so `python3` comes from the FreeBSD repository first, and `pkg upgrade` does not offer new releases.

`SHA256SUMS` and the build provenance attestations cover every package, as they do `findbig.py` (below).

Or clone the repository and link the script into a directory on your `PATH`:

```
git clone https://github.com/cdf-eagles/py-findbig.git
ln -s "$PWD/py-findbig/findbig.py" ~/bin/findbig.py
```

Or download `findbig.py` and `SHA256SUMS` from a [release](https://github.com/cdf-eagles/py-findbig/releases) and check them before use: `shasum -a 256 -c SHA256SUMS` on macOS (`sha256sum -c SHA256SUMS` elsewhere), and `gh attestation verify findbig.py --repo cdf-eagles/py-findbig` for the build provenance.

## What it reports

* Each row is a file or directory under the search path, largest first, up to the number of lines asked for. Of two entries the same size, a directory is listed before what is in it.
* A directory's size is the total of the files below it; the size the file system reports for the directory itself is not counted, so an empty directory shows `0B`. A hard-linked file counts once for each of its names.
* Sizes are apparent sizes (the bytes in each file), shown in bytes, then kilobytes (K), megabytes (M), gigabytes (G), or terabytes (T) of 1024 each. They are not what `du` shows: `du` counts disk blocks by default, and counts each directory's own size and each hard-linked file once.
* Symbolic links are listed but not followed, and count as 0 bytes. The search path itself may be a symbolic link to a directory.
* A file or directory that vanishes during the walk, or a directory that cannot be read, counts as 0 bytes, and an age that cannot be read shows as `-`.
* The second column is the time since the entry was created, labelled `Created`, on systems that record a birth time, such as macOS and FreeBSD; a file system that records none shows `-`. Elsewhere, such as on Linux, it is the time since the entry's inode last changed, labelled `Changed`.
* Ages are read from each entry itself, so a symbolic link shows its own ages, not its target's.
* With `--csv`, which is off by default, the output is comma-separated values (CSV) instead of the table, for a spreadsheet or another tool: a header row, then one row per entry with the full path (never cut to the terminal's width), the size in whole bytes, and the creation (or change) and modification times as Coordinated Universal Time (UTC) timestamps in ISO 8601 form. The third column is named `created` or `changed` by the same rule as the table's second column, and a time that cannot be read or is not recorded is empty. A path holding a comma, a quote, or a line break is quoted.
* With `--json`, which is off by default and cannot be combined with `--csv`, the output is one JSON array of objects instead of the table, for `jq` or another tool: each object has the same fields as the CSV columns, with the same names (`path`, `size_bytes`, `created` or `changed`, and `modified`). The size is a whole number of bytes, and a time that cannot be read or is not recorded is `null`.

## Example Usage

### Help

The default number of lines is the terminal's height less 5: a standard 80x24 terminal prints 19 lines. `-n` takes a whole number greater than 0; anything else is a usage error. `-V` (`--version`) prints the release the script belongs to, the same version as its GitHub release tag, and the help shows it too.

```
$ findbig.py -h
usage: findbig.py [-h] [-n LINES] [--csv | --json] [-V] [search_path]

This script recursively finds the largest files/directories in the current
working directory (default) or the specified directory.

positional arguments:
  search_path      If provided, program will search the provided path instead
                   of the current working directory. (default: ./)

options:
  -h, --help       show this help message and exit
  -n, --num LINES  The number of lines to display. (default: 19)
  --csv            Write comma-separated values (path, size in bytes, and UTC
                   times) instead of the table. (default: False)
  --json           Write a JSON array of objects (path, size in bytes, and UTC
                   times) instead of the table. (default: False)
  -V, --version    Show the release version (v0.5.0) and exit.

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

### CSV output

This example ran on Linux, where the third column is `changed`, in a tree like the one above with a file whose name holds a comma.

```
$ findbig.py --csv
path,size_bytes,changed,modified
./,120586240,2026-11-14T22:23:38+00:00,2026-11-14T22:23:38+00:00
./a,65011712,2026-11-14T22:23:38+00:00,2026-11-14T22:23:38+00:00
./a/1,54525952,2026-11-14T22:23:38+00:00,2026-11-14T22:23:38+00:00
./a/1/file1,54525952,2026-11-14T22:23:38+00:00,2026-11-14T22:23:38+00:00
./b,45088768,2026-11-14T22:23:38+00:00,2026-11-14T22:23:38+00:00
./b/2,45088768,2026-11-14T22:23:38+00:00,2026-11-14T22:23:38+00:00
./b/2/file2,45088768,2026-11-14T22:23:38+00:00,2026-11-14T22:23:38+00:00
./a/filea,10485760,2026-11-14T22:23:38+00:00,2026-11-14T22:23:38+00:00
./c,10485760,2026-11-14T22:23:38+00:00,2026-11-14T22:23:38+00:00
"./c/file, with a comma",10485760,2026-11-14T22:23:38+00:00,2026-11-14T22:23:38+00:00
```

### JSON output

This example ran on Linux, where the creation field is `changed`, in the tree above.

```
$ findbig.py --json -n 3
[
  {
    "path": "./",
    "size_bytes": 167772160,
    "changed": "2026-11-15T00:53:52+00:00",
    "modified": "2026-11-15T00:53:52+00:00"
  },
  {
    "path": "./a",
    "size_bytes": 98566144,
    "changed": "2026-11-15T00:53:52+00:00",
    "modified": "2026-11-15T00:53:52+00:00"
  },
  {
    "path": "./a/1",
    "size_bytes": 88080384,
    "changed": "2026-11-15T00:53:52+00:00",
    "modified": "2026-11-15T00:53:52+00:00"
  }
]
```

`jq` reads the array directly, for example to list every entry over 40,000,000 bytes:

```
$ findbig.py --json | jq -r '.[] | select(.size_bytes > 40000000) | "\(.size_bytes)\t\(.path)"'
167772160	./
98566144	./a
88080384	./a/1
58720256	./b
54525952	./a/1/file1
48234496	./b/2
45088768	./b/2/file2
```

## Development and CI

See [CONTRIBUTING.md](CONTRIBUTING.md) to set up the checks locally.

The `CI` workflow (`.github/workflows/ci.yaml`) runs on every pull request to `main`, every push to `main`, and weekly. It has these jobs:

* `Lint` runs shellcheck over `scripts/`, yamllint, then every pre-commit hook over all files: black, isort, flake8, pylint, actionlint, the GitHub workflow and Dependabot schema checks, and the private-key checks.
* `Secret scan` runs gitleaks over the full git history.
* `Test` runs the unit tests in `tests/` with `python3 -m unittest`.
* `Packages` runs the reusable `Packages` workflow (`.github/workflows/packages.yaml`). Its `Linux` job builds the `.deb`, `.rpm`, and `.apk` with nFPM (`packaging/nfpm.yaml`, `packaging/build-linux-packages.sh`), signing the `.apk` with a key made for the run, then installs, removes, and reinstalls each one in a Debian, AlmaLinux, and Alpine Linux container and runs it as the unprivileged user `nobody` (`packaging/test-linux-packages.sh`). Its `FreeBSD` job lints the manual page with `mandoc`, then builds, installs, runs, and removes the FreeBSD package in a FreeBSD virtual machine (`packaging/freebsd/build-pkg.sh`).
* `Tool drift` runs weekly and opens an issue when a pinned tool has a newer release.

The tests need only the Python standard library (and `git` for the release script tests): `python3 -m unittest discover -s tests -t .` runs them locally.

## Releases

Work is squash merged into `main` through pull requests from `fix/`, `feat/`, `major/`, `build/`, or `ignore/` branches. A release is cut from `main`:

1. `scripts/next-version.sh` proposes the next version from the branch prefixes of the pull requests merged since the last release tag (it looks them up with the GitHub CLI, `gh`): `major/` bumps the major version, `feat/` the minor, and `fix/` the patch.
2. `__version__` in `findbig.py` must name that version, since `--version` and `--help` show it; a `build/` pull request raises it when it does not.
3. A signed release candidate tag `vX.Y.Z-rc.N` on that `main` commit runs the `Release` workflow (`.github/workflows/release.yaml`). It checks that the tag is annotated, verified-signed, on `main`, and matches `__version__`, runs the unit tests, builds and tests the packages through the `Packages` workflow with the `.apk` signed by the `APK_SIGNING_KEY` secret (which must match `packaging/alpine/py-findbig.rsa.pub`), and publishes a pre-release holding `findbig.py`, the packages, the `.apk` public key, `SHA256SUMS`, and build provenance attestations.
4. After the release candidate is proven, the same commit is tagged `vX.Y.Z`. The workflow publishes the release candidate's own files as the release, after checking them against their checksums and attestations.
5. The workflow's `homebrew` job then opens a pull request on [homebrew-tap](https://github.com/cdf-eagles/homebrew-tap) that points `Formula/findbig.rb` at the release's source archive (`scripts/update-homebrew-formula.sh pr`). It signs in as a GitHub App installed only on the tap, whose client ID is the `HOMEBREW_TAP_APP_CLIENT_ID` repository variable and whose private key is the `HOMEBREW_TAP_APP_PRIVATE_KEY` secret, with a token limited to the tap's contents and pull requests. The tap's CI audits, installs, and tests the new formula, and the pull request is merged by hand once it passes.

`build/`, `dependabot/`, and `ignore/` pull requests do not bump the version and ship with the next release.

Tool versions live in one place each: Python tools in `ci/requirements.txt`, pre-commit hooks in `.pre-commit-config.yaml`, the test containers' images in `packaging/test/*/Dockerfile`, the gitleaks release in the CI workflow's `env:` block and the nFPM release in the Packages workflow's, each with its SHA-256 checksum, and the FreeBSD release in the Packages workflow's `FREEBSD_RELEASE`. Dependabot updates the first three; the weekly Tool drift job opens an issue when gitleaks or nFPM has a newer release, and the FreeBSD release is raised by hand.
