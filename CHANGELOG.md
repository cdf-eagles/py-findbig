# Changelog

- 2026-11-22
  - The Linux packages are served from the account's package repository, `packages` (<https://cdf-eagles.github.io/packages/>), so `apt`, `dnf`, and `apk` install `findbig` and offer each new release as an upgrade; the README's Installation section gives the setup. Found internally from backlog item 580.
  - A final release opens a pull request on `packages` that adds the release's `.deb`, `.rpm`, and `.apk`, with their SHA-256 checksums and release candidate tag, to `sources/py-findbig.txt` (`scripts/update-package-repository.sh`). The `Release` workflow signs in as a GitHub App installed only on that repository.
  - The `.rpm` is signed with the package repository's OpenPGP key (`PACKAGES_SIGNING_KEY`, public half `packaging/packages-signing.asc`), and the package tests check its signature on AlmaLinux 9, newly tested, and AlmaLinux 10.
- 2026-11-18
  - A Snyk job in continuous integration (CI) tests the Python tools pinned in `ci/requirements.txt`, which Snyk's repository import skips, and fails on any high or critical issue, a scan error, or a missing `SNYK_TOKEN` secret. The Snyk CLI 1.1308.4 is downloaded from its GitHub release and verified by its checksum; found internally from backlog item 572.
  - The weekly Tool drift job calls the Tool drift workflow v1.1.1, which also checks the `SNYK_VERSION` pin against the latest Snyk CLI release.
- 2026-11-15
  - SonarCloud analyses the repository from continuous integration (CI) instead of its automatic analysis, so the analysis now carries test coverage and the quality gate's coverage condition on new code applies. The new `SonarCloud` job runs the unit tests under coverage.py and runs pysonar, pinned in `ci/requirements.txt` with coverage.py, reading its token from Amazon Web Services (AWS) Systems Manager Parameter Store through OpenID Connect (OIDC). Found internally from backlog item 582.
  - A final release opens a pull request on the account's Homebrew tap (`homebrew-tap`) that points the `findbig` formula at the release's source archive (`scripts/update-homebrew-formula.sh`). The `Release` workflow signs in as a GitHub App installed only on the tap, so the token reaches nothing else and the pull request runs the tap's CI. Found internally from backlog item 577.
  - The README's Installation section adds Homebrew: `brew install cdf-eagles/tap/findbig` installs the command and its manual page on macOS.
  - `__version__` is 0.6.0 for the v0.6.0 release, the first whose final tag opens the Homebrew tap's formula pull request; the README's package file names and help text follow it.
- 2026-11-14
  - This changelog starts, filled in from the repository's history. Found internally from backlog item 566.
  - A search path that does not exist or is not a directory now stops with a usage error instead of a traceback from an empty result list. Found internally from backlog item 567.
  - Dependabot raised the weekly Tool drift job's reusable workflow from v1.0.0 to v1.1.0.
  - A file or directory that vanishes during the walk, or a subdirectory that cannot be read, no longer stops the script with a `KeyError` or `FileNotFoundError`: such entries count as 0 bytes, and an age that cannot be read shows as `-`. Fixes issue #14; found internally from backlog item 568.
  - A file that vanishes no longer takes the size of the file listed before it, and a search path that is a symbolic link to a directory no longer fails with an `UnboundLocalError`.
  - A symbolic link whose target is gone no longer stops the script with a `FileNotFoundError`: ages are read from the entry itself (`os.lstat`), so a link shows its own age, as it already counted as 0 bytes instead of its target's size.
  - `-n` takes a whole number greater than 0 and refuses anything else with a usage error, where `-n 0` used to end in an `AttributeError`; error handling that could never run is gone. Found internally from backlog item 569.
  - A directory's size is the total of the files below it, without the size the file system reports for each directory, so an empty directory shows `0B`.
  - The creation column shows the birth time where the operating system records one, as on macOS and FreeBSD, and elsewhere is labelled `Changed`, since it shows the inode change time; it was labelled `Created` everywhere.
  - The walk reads each file once with `os.scandir`, where it used to read each file and directory twice, and keeps only the largest entries instead of sorting all of them; on a 271,126-entry tree it took 0.72 times as long.
  - The table's columns line up, and a short path no longer widens the name column to the terminal's width.
  - The README's help text and examples match the script, and it explains what the sizes and ages mean and how to install the script; the header comment keeps only the project link and the credit to the Perl script.
  - Tagged `v0.3.0` with these changes.
  - A `--csv` option, off by default, writes comma-separated values instead of the table: the full path, the size in whole bytes, and the creation (or change) and modification times as UTC timestamps, with a header row. From backlog item 571.
  - `-V` (`--version`) prints the release version, `v0.4.0`, which `--help` shows too; `CONTRIBUTING.md` says to raise it before each release is tagged.
  - Releases follow zpool-status-exporter's process: the branch prefix (`major/`, `feat/`, `fix/`) decides the bump, `scripts/next-version.sh` proposes the version, a signed `vX.Y.Z-rc.N` tag publishes a pre-release with `findbig.py`, `SHA256SUMS`, and a build provenance attestation, and a signed `vX.Y.Z` tag promotes it. The `Release` workflow refuses a tag that does not match `__version__` (`scripts/check-release-version.sh`), and the `Lint` job runs shellcheck over `scripts/`. From backlog item 571.
  - A `--json` option, off by default and not allowed with `--csv`, writes one JavaScript Object Notation (JSON) array of objects instead of the table, with the CSV's fields and names (`path`, `size_bytes`, `created` or `changed`, and `modified`) and `null` for a time that cannot be read or is not recorded. From backlog item 575.
  - `__version__` is `0.5.0` for the next minor release, and a unit test checks that the README's help block matches `--help` on Python 3.13 and later.
  - Each release publishes packages that install the command as `findbig` with a manual page, `findbig.1`, and depend on `python3`: a `.deb`, an `.rpm`, and a signed `.apk` built with nFPM, and a FreeBSD 15 package, all covered by `SHA256SUMS` and the attestations. From backlog items 576 and 578.
  - A `Packages` CI job builds every package and installs, runs, and removes it in a Debian, AlmaLinux, or Alpine Linux container (running it as the unprivileged user `nobody`) or a FreeBSD virtual machine; a unit test checks the manual page against the options, and Dependabot raises the test images.

- 2026-11-12
  - Removed the SonarCloud analysis workflow, which was disabled in GitHub Actions and had never run; SonarCloud's Automatic Analysis already scans every push and pull request. Found internally from backlog item 353.

- 2026-11-06
  - Dependabot raised the flake8 pre-commit hook from 7.4.1 to 7.5.0 and the SonarSource/sonarqube-scan-action pin from 8.4.0 to 8.4.1.

- 2026-10-30
  - Dependabot raised check-jsonschema from 0.38.2 to 0.39.0, as both the pre-commit hook and the continuous integration (CI) Python tool, and the SonarSource/sonarqube-scan-action pin from 8.3.0 to 8.4.0.

- 2026-10-24
  - The CI secret scan downloads gitleaks 8.30.1, up from 8.21.2, verified by its checksum. Found internally from backlog item 381.
  - Dependabot raised the black pre-commit hook from 26.3.1 to 26.10.1, the flake8 hook from 7.3.0 to 7.4.1, and the SonarSource/sonarqube-scan-action pin from 7.2.0 to 8.3.0.

- 2026-10-23
  - One required CI workflow replaces the pylint workflow, which linted only the added lines of changed Python files: its Lint job runs yamllint, every pre-commit hook, and pylint over every Python file, and its Secret scan job runs checksum-verified gitleaks over the history of the checked-out commit. Found internally from backlog items 353, 357, 361, and 380.
  - The gitleaks download accepts only Hypertext Transfer Protocol Secure (HTTPS) with Transport Layer Security (TLS) 1.2 or later, so a redirect cannot drop it to an unencrypted connection. Found internally from backlog item 357.
  - Python tools are pinned in `ci/requirements.txt`, the isort hook moved from 9.0.0a3 to 9.0.2, pre-commit adds the actionlint and check-dependabot hooks, and Dependabot opens weekly grouped updates for the actions, the Python tools, and the hooks.
  - A pre-push hook runs gitleaks over the commits being pushed, and a weekly Tool drift job opens an issue when a pinned tool has a newer release.
  - The SonarCloud job checks out the code before scanning, since it had been scanning an empty workspace, and skips pull requests from forks.
  - The README describes the CI jobs and where each tool version lives, and `CONTRIBUTING.md` gives the local setup on macOS.

- 2026-07-29
  - The pylint workflow's checkout action is pinned to its latest release.

- 2026-04-28
  - The pre-commit hooks moved to check-jsonschema 0.37.1, black 26.3.1, and isort 9.0.0a3, and the pylint workflow's actions are pinned to their latest commits.
  - The SonarCloud workflow uses SonarSource/sonarqube-scan-action in place of the deprecated SonarSource/sonarcloud-github-action.

- 2026-04-22
  - The script's top-level code moved into a `main()` function.

- 2025-10-03
  - Applied black's formatting, removed the `noqa` comments and some unneeded code, and set the line length for black and pylint to 79, flake8's default.
  - Fixed the `print_table()` call, which passed the data in a form the function did not expect.
  - Tagged `v0.2.1` with these fixes.

- 2025-10-02
  - First release, tagged `v0.2`: `findbig.py`, a Python 3 implementation of Jason Fesler's Perl 5 findbig script, which lists the largest files and directories under the current or a given directory.
  - pre-commit runs black, isort, flake8, pylint, the GitHub workflow schema check, and the private-key and secret checks, with a line length of 80.
  - A pylint workflow lints the changed Python files of pull requests and pushes to `main`, with its actions pinned by commit hash, and a SonarCloud workflow analyzes the code.
  - The README shows usage examples and badges for pre-commit, the lint workflow, and SonarCloud, and the repository has a Berkeley Software Distribution (BSD) 3-Clause license, `CONTRIBUTING.md`, and a `CODEOWNERS` file.

- 2025-09-30
  - Created the repository with the license and `.gitignore`.
