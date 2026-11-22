#!/bin/sh
#
# Install each Linux package in a container of its distribution, remove
# and reinstall it, then run the installed command and check its manual
# page as the unprivileged user nobody. The AlmaLinux tests first check the
# .rpm's signature against the OpenPGP public key. Each test is a docker
# build that fails when a step fails.
#
# Usage: test-linux-packages.sh <version> <package-dir> <apk-public-key> <rpm-public-key>
#
# Run from the repository root. The paths are relative to it, since they
# are copied from the build context.

set -eu

if [ "$#" -ne 4 ]; then
    echo "usage: $0 <version> <package-dir> <apk-public-key> <rpm-public-key>" >&2
    exit 64
fi

version=$1
pkgdir=$2
pubkey=$3
rpmkey=$4

for distribution in debian almalinux almalinux9 alpine; do
    echo "== ${distribution}"
    docker build --no-cache --progress plain \
        --build-arg VERSION="${version}" \
        --build-arg PKGDIR="${pkgdir}" \
        --build-arg APK_PUBKEY="${pubkey}" \
        --build-arg RPM_PUBKEY="${rpmkey}" \
        --file "packaging/test/${distribution}/Dockerfile" .
done
