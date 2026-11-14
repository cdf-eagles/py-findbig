# Contributing

## Local setup (macOS)

* Create a virtual environment with the pinned tools, and install the Git hooks
  * `python3 -m venv .venv`
  * `.venv/bin/pip install -r ci/requirements.txt`
  * `PATH="$PWD/.venv/bin:$PATH" pre-commit install`
* Run every check over all files
  * `PATH="$PWD/.venv/bin:$PATH" pre-commit run --all-files`
  * `PATH="$PWD/.venv/bin:$PATH" yamllint --strict .`
  * `python3 -m unittest discover -s tests -t .`

The hooks run black, isort, flake8, pylint, actionlint, the secret checks, and the GitHub workflow and Dependabot schema checks. A `pre-push` hook also runs gitleaks over the commits being pushed, so install gitleaks locally (`brew install gitleaks`).

## Where tool versions live

* Python tools (pre-commit, pylint, yamllint, check-jsonschema, shellcheck-py): `ci/requirements.txt`, exact `==` pins.
* Pre-commit hooks: the `rev:` of each hook in `.pre-commit-config.yaml`; run `pre-commit autoupdate` to refresh them.
* gitleaks in CI: `GITLEAKS_VERSION` and `GITLEAKS_SHA256` in `.github/workflows/ci.yaml`.

Dependabot opens weekly pull requests for all of these.

## Branches and releases

* Work goes to `main` only through squash-merged pull requests. The branch prefix decides the next release's version bump: `major/` (major), `feat/` (minor), `fix/` (patch); `build/`, `ignore/`, and Dependabot's branches do not bump and ship with the next release.
* Cutting a release (see the README's Releases section):
  * `scripts/next-version.sh` proposes the next version and prints the tag commands; it needs the GitHub CLI (`gh`) to read the squash-merged pull requests.
  * If `__version__` in `findbig.py` differs from the proposal, a `build/` pull request raises it first, with its changelog lines.
  * Tag the proposal's release candidate with the signed `git tag -s vX.Y.Z-rc.N` command it prints, on that `main` commit, and push the tag. The Release workflow refuses a tag that is not annotated, not verified-signed, not on `main`, or does not match `__version__` (`scripts/check-release-version.sh`).
  * After checking the pre-release's `findbig.py`, push the signed `vX.Y.Z` tag on the same commit; the workflow republishes the release candidate's own files.
* The release scripts are POSIX `sh`, shellcheck-clean, and run on macOS and Linux; their tests are in `tests/test_release_scripts.py`.
