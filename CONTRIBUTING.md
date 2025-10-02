# macOS
* Install pre-commit and packages for code quality checks
  * `brew install pre-commit flake8 isort black pylint`
* Create pre-commit configuration
  * `pre-commit sample-config > .pre-commit-config.yaml`
* Customize the pre-commit configuration
```
# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks
repos:
  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.34.0
    hooks:
      - id: check-github-workflows
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
      - id: detect-private-key
      - id: requirements-txt-fixer
  - repo: https://github.com/sirwart/ripsecrets
    rev: v0.1.11
    hooks:
      - id: ripsecrets
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.9.0
    hooks:
      - id: black
        language_version: python3.13
        args: ["--line-length=120"]
  - repo: https://github.com/pycqa/isort
    rev: 6.1.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.3.0
    hooks:
      - id: flake8
  - repo: local
    hooks:
      - id: pylint
        name: pylint
        entry: pylint
        language: system
        types: [python]
        require_serial: true
        args:
          [
            "-rn", # only display messages
            "--rcfile=.pylintrc", # project pylint configuration file
          ]
```
* Run pre-commit autoupdate to ensure latest revisions of repos are set up
  * `pre-commit autoupdate`
* Install the pre-commit git hook scripts
  * `pre-commit install`
* Test your pre-commit environment
  * `pre-commit run --all-files`
