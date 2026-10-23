# Contributing

## Local setup (macOS)

* Create a virtual environment with the pinned tools, and install the Git hooks
  * `python3 -m venv .venv`
  * `.venv/bin/pip install -r ci/requirements.txt`
  * `PATH="$PWD/.venv/bin:$PATH" pre-commit install`
* Run every check over all files
  * `PATH="$PWD/.venv/bin:$PATH" pre-commit run --all-files`
  * `PATH="$PWD/.venv/bin:$PATH" yamllint --strict .`

The hooks run black, isort, flake8, pylint, actionlint, the secret checks, and the GitHub workflow and Dependabot schema checks. A `pre-push` hook also runs gitleaks over the commits being pushed, so install gitleaks locally (`brew install gitleaks`).

## Where tool versions live

* Python tools (pre-commit, pylint, yamllint, check-jsonschema, shellcheck-py): `ci/requirements.txt`, exact `==` pins.
* Pre-commit hooks: the `rev:` of each hook in `.pre-commit-config.yaml`; run `pre-commit autoupdate` to refresh them.
* gitleaks in CI: `GITLEAKS_VERSION` and `GITLEAKS_SHA256` in `.github/workflows/ci.yaml`.

Dependabot opens weekly pull requests for all of these.
