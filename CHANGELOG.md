# Changelog

- 2026-11-14
  - This changelog starts, filled in from the repository's history. Found internally from backlog item 566.
  - A search path that does not exist or is not a directory now stops with a usage error instead of a traceback from an empty result list. Found internally from backlog item 567.
  - Dependabot raised the weekly Tool drift job's reusable workflow from v1.0.0 to v1.1.0.

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
