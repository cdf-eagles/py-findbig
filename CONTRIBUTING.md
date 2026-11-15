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
* nFPM: `NFPM_VERSION` and `NFPM_SHA256` in `.github/workflows/packages.yaml`, from the release's `checksums.txt`.
* Package test images: the `FROM` line of each `packaging/test/*/Dockerfile`.
* The FreeBSD release the package is built and tested on: `FREEBSD_RELEASE` in `.github/workflows/packages.yaml`, raised by hand.

Dependabot opens weekly pull requests for the Python tools, the hooks, the test images, and the actions; the weekly Tool drift job opens an issue for gitleaks and nFPM.

## Branches and releases

* Work goes to `main` only through squash-merged pull requests. The branch prefix decides the next release's version bump: `major/` (major), `feat/` (minor), `fix/` (patch); `build/`, `ignore/`, and Dependabot's branches do not bump and ship with the next release.
* Cutting a release (see the README's Releases section):
  * `scripts/next-version.sh` proposes the next version and prints the tag commands; it needs the GitHub CLI (`gh`) to read the squash-merged pull requests.
  * If `__version__` in `findbig.py` differs from the proposal, a `build/` pull request raises it first, with its changelog lines.
  * Tag the proposal's release candidate with the signed `git tag -s vX.Y.Z-rc.N` command it prints, on that `main` commit, and push the tag. The Release workflow refuses a tag that is not annotated, not verified-signed, not on `main`, or does not match `__version__` (`scripts/check-release-version.sh`).
  * After checking the pre-release's `findbig.py`, push the signed `vX.Y.Z` tag on the same commit; the workflow republishes the release candidate's own files.
* A final release also opens a pull request on the Homebrew tap (`scripts/update-homebrew-formula.sh`), through a GitHub App installed only on `homebrew-tap` with Contents and Pull requests read and write. Its client ID is the `HOMEBREW_TAP_APP_CLIENT_ID` repository variable and its private key the `HOMEBREW_TAP_APP_PRIVATE_KEY` repository secret. Merge that pull request once the tap's CI passes.
* The release scripts are POSIX `sh`, shellcheck-clean, and run on macOS and Linux; their tests are in `tests/test_release_scripts.py`.

## Packages

* `packaging/` builds the `.deb`, `.rpm`, and `.apk` (nFPM) and the FreeBSD package; `docs/findbig.1` is the manual page every package installs. A unit test fails when an option is missing from the page or the page names one the script lacks.
* The `.apk` is signed with the `APK_SIGNING_KEY` repository secret, whose public half is `packaging/alpine/py-findbig.rsa.pub`; a release fails when they do not match. Pull request runs sign with a key made for the run.
* To build the Linux packages locally, put `nfpm` on `PATH` and an RSA key at `build/apk-signing.rsa` (`openssl genrsa -out build/apk-signing.rsa 2048`), then run `sh packaging/build-linux-packages.sh "$(python3 findbig.py --version | sed 's/.* v//')" findbig.py dist`. With Docker, `sh packaging/test-linux-packages.sh <version> dist <public key>` installs and runs them.
