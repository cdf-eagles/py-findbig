#!/bin/sh
#
# Build the FreeBSD package of findbig. Runs on FreeBSD only.
#
# Usage: build-pkg.sh <version> <findbig.py> <output-dir>
#
# Run from the repository root. A release candidate suffix in the version
# is rewritten to the form pkg(8) accepts: 1.2.0-rc.1 becomes 1.2.0.r1.

set -eu

if [ "$#" -ne 3 ]; then
    echo "usage: $0 <version> <findbig.py> <output-dir>" >&2
    exit 64
fi

version=${1#v}
script=$2
outdir=$3

here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "${here}/../.." && pwd)

version=$(printf '%s\n' "${version}" | sed -e 's/-rc\.\([0-9][0-9]*\)$/.r\1/')
case ${version} in
    *[!0-9A-Za-z._]* | '')
        echo "unsupported version: ${version}" >&2
        exit 65
        ;;
    *) ;;
esac

if [ ! -f "${script}" ]; then
    echo "script not found: ${script}" >&2
    exit 66
fi

stage=$(mktemp -d)
trap 'rm -rf "${stage}"' EXIT HUP INT TERM

install -d "${stage}/root/usr/local/bin" \
    "${stage}/root/usr/local/share/man/man1" \
    "${stage}/root/usr/local/share/doc/findbig"
install -m 0555 "${script}" "${stage}/root/usr/local/bin/findbig"
gzip -9nc "${root}/docs/findbig.1" \
    > "${stage}/root/usr/local/share/man/man1/findbig.1.gz"
install -m 0444 "${root}/LICENSE" \
    "${stage}/root/usr/local/share/doc/findbig/LICENSE"

sed -e "s/%%VERSION%%/${version}/" "${here}/+MANIFEST.in" > "${stage}/+MANIFEST"

cat > "${stage}/plist" <<PLIST
@(root,wheel,0555) bin/findbig
@(root,wheel,0444) share/man/man1/findbig.1.gz
@(root,wheel,0444) share/doc/findbig/LICENSE
PLIST

mkdir -p "${outdir}"
pkg create -M "${stage}/+MANIFEST" -p "${stage}/plist" -r "${stage}/root" -o "${outdir}"
