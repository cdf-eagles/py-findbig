#!/bin/sh
#
# Install each Linux package in a container of its distribution, run the
# installed command, check its manual page, and remove the package. Each
# test is a docker build that fails when a step fails.
#
# Usage: test-linux-packages.sh <version> <package-dir> <apk-public-key>
#
# Run from the repository root. Both paths are relative to it, since they
# are copied from the build context.

set -eu

if [ "$#" -ne 3 ]; then
    echo "usage: $0 <version> <package-dir> <apk-public-key>" >&2
    exit 64
fi

version=$1
pkgdir=$2
pubkey=$3

for distribution in debian almalinux alpine; do
    echo "== ${distribution}"
    docker build --no-cache --progress plain \
        --build-arg VERSION="${version}" \
        --build-arg PKGDIR="${pkgdir}" \
        --build-arg APK_PUBKEY="${pubkey}" \
        --file "packaging/test/${distribution}/Dockerfile" .
done
