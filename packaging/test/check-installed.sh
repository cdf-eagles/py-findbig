#!/bin/sh
#
# Check an installed findbig: its version, its manual page, and one run
# whose JSON output Python reads back.
#
# Usage: check-installed.sh <version> <manual-page-path>

set -eu

version=$1
manpage=$2

reported=$(findbig --version)
if [ "${reported}" != "findbig v${version}" ]; then
    echo "findbig reports '${reported}', not v${version}" >&2
    exit 1
fi

if [ ! -f "${manpage}" ]; then
    echo "no manual page at ${manpage}" >&2
    exit 1
fi

count=$(findbig --json -n 3 /usr | python3 -c \
    'import json, sys; print(len(json.load(sys.stdin)))')
if [ "${count}" != 3 ]; then
    echo "findbig --json -n 3 /usr gave ${count} entries, not 3" >&2
    exit 1
fi

echo "findbig v${version} installed, documented, and ran"
