#!/bin/sh
# Check that a release tag names the version in findbig.py, so a release
# never ships a script whose --version reports another release.
#
# TAG is vX.Y.Z or vX.Y.Z-rc.N; a release candidate carries the plain X.Y.Z
# version so it can be promoted unchanged. Exits 0 when the versions match,
# 1 when they differ, and 2 on a usage error, an unsupported tag, or a file
# without exactly one __version__ line.
#
# Usage: scripts/check-release-version.sh TAG [FILE]   (default FILE: findbig.py)
set -eu

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
	echo "usage: check-release-version.sh TAG [FILE]" >&2
	exit 2
fi
tag=$1
file=${2:-findbig.py}

case "$tag" in
	v[0-9]*.[0-9]*.[0-9]*-rc.[0-9]*)
		version=${tag#v}
		version=${version%-rc.*}
		;;
	v[0-9]*.[0-9]*.[0-9]*) version=${tag#v} ;;
	*)
		echo "check-release-version: unsupported tag ${tag}" >&2
		exit 2
		;;
esac
case "$version" in
	*[!0-9.]*)
		echo "check-release-version: unsupported tag ${tag}" >&2
		exit 2
		;;
esac

found=$(sed -n 's/^__version__ = "\([^"]*\)"$/\1/p' "$file" 2> /dev/null || true)
count=$(printf '%s' "$found" | grep -c '^' || true)
if [ "$count" -ne 1 ]; then
	echo "check-release-version: expected one __version__ line in ${file}, found ${count}" >&2
	exit 2
fi
if [ "$found" != "$version" ]; then
	echo "check-release-version: ${tag} names ${version}, but ${file} has __version__ ${found}" >&2
	exit 1
fi
echo "check-release-version: ${tag} matches __version__ ${found} in ${file}"
