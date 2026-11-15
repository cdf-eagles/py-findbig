#!/bin/sh
#
# Build the .deb, .rpm, and .apk packages of findbig with nFPM.
#
# Usage: build-linux-packages.sh <version> <findbig.py> <output-dir>
#
# Run from the repository root with nfpm on PATH and the .apk signing key,
# an RSA private key in PEM form, at build/apk-signing.rsa.

set -eu

if [ "$#" -ne 3 ]; then
    echo "usage: $0 <version> <findbig.py> <output-dir>" >&2
    exit 64
fi

version=$1
script=$2
outdir=$3

case ${version} in
    *[!0-9.]* | '')
        echo "unsupported version: ${version}" >&2
        exit 65
        ;;
    *) ;;
esac

reported=$(python3 "${script}" --version)
if [ "${reported}" != "$(basename "${script}") v${version}" ]; then
    echo "${script} reports '${reported}', not v${version}" >&2
    exit 65
fi

if [ ! -f build/apk-signing.rsa ]; then
    echo "no .apk signing key at build/apk-signing.rsa" >&2
    exit 66
fi

mkdir -p build/stage "${outdir}"
install -m 0755 "${script}" build/stage/findbig
gzip -9nc docs/findbig.1 > build/stage/findbig.1.gz

for packager in deb rpm apk; do
    VERSION=${version} nfpm package --packager "${packager}" \
        --config packaging/nfpm.yaml --target "${outdir}/"
done
