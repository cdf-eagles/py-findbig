#!/bin/sh
# Add a release's Linux packages to the account's package repository.
#
# lines prints the manifest lines for a release from its SHA256SUMS file:
# one "<tag> <release candidate tag> <file> <sha256>" line for each of the
# .deb, .rpm, and .apk, and refuses a checksum file that lacks one of them
# or holds a malformed entry. pr reads sources/py-findbig.txt from the
# package repository, appends the release's lines on a new branch through
# the GitHub API, and opens a pull request; it needs gh with a token that
# may write the package repository's contents and pull requests. It exits 0
# without a change when the list already holds the tag.
#
# Exits 0 on success, 1 when a step fails, and 2 on a usage error.
#
# Usage: scripts/update-package-repository.sh lines TAG RC_TAG SHA256SUMS
#        scripts/update-package-repository.sh pr TAG RC_TAG SHA256SUMS
set -eu

PACKAGES_REPO=${PACKAGES_REPO:-cdf-eagles/packages}
LIST_PATH=sources/py-findbig.txt

usage() {
	echo "usage: update-package-repository.sh lines TAG RC_TAG SHA256SUMS" >&2
	echo "       update-package-repository.sh pr TAG RC_TAG SHA256SUMS" >&2
	exit 2
}

# check_tags TAG RC_TAG: a final tag vX.Y.Z and a release candidate of it.
check_tags() {
	case "$1" in
	v[0-9]*.[0-9]*.[0-9]*) ;;
	*)
		echo "unsupported tag $1" >&2
		exit 2
		;;
	esac
	case "$1" in
	*[!v0-9.]*)
		echo "unsupported tag $1" >&2
		exit 2
		;;
	*) ;;
	esac
	case "$2" in
	"$1"-rc.[0-9]*) ;;
	*)
		echo "unsupported release candidate tag $2 for $1" >&2
		exit 2
		;;
	esac
	case "${2#"$1"-rc.}" in
	*[!0-9]*)
		echo "unsupported release candidate tag $2 for $1" >&2
		exit 2
		;;
	*) ;;
	esac
}

lines() {
	[ $# -eq 3 ] || usage
	tag=$1
	rc=$2
	sums=$3
	check_tags "$tag" "$rc"
	[ -f "$sums" ] || {
		echo "no checksum file: $sums" >&2
		exit 2
	}
	version=${tag#v}
	for file in "findbig_${version}_all.deb" "findbig-${version}-1.noarch.rpm" "findbig_${version}_noarch.apk"; do
		n=$(awk -v f="$file" '$2 == f || $2 == "*" f { n++ } END { print n + 0 }' "$sums")
		if [ "$n" -ne 1 ]; then
			echo "expected one ${file} line in $sums, found $n" >&2
			exit 2
		fi
		sum=$(awk -v f="$file" '$2 == f || $2 == "*" f { print $1 }' "$sums")
		case "$sum" in
		*[!0-9a-f]* | "")
			echo "not a SHA-256 checksum for ${file}: $sum" >&2
			exit 2
			;;
		*) ;;
		esac
		if [ "${#sum}" -ne 64 ]; then
			echo "not a SHA-256 checksum for ${file}: $sum" >&2
			exit 2
		fi
		printf '%s %s %s %s\n' "$tag" "$rc" "$file" "$sum"
	done
}

pr() {
	[ $# -eq 3 ] || usage
	tag=$1
	rc=$2
	sums=$3
	version=${tag#v}
	work=$(mktemp -d)
	trap 'rm -rf "$work"' EXIT
	lines "$tag" "$rc" "$sums" >"$work/new"

	gh api -H "Accept: application/vnd.github.raw+json" \
		"repos/${PACKAGES_REPO}/contents/${LIST_PATH}" >"$work/list"
	blob=$(gh api "repos/${PACKAGES_REPO}/contents/${LIST_PATH}" --jq .sha)
	if grep -q "^${tag} " "$work/list"; then
		echo "${PACKAGES_REPO} ${LIST_PATH} already lists ${tag}; nothing to do"
		return 0
	fi
	cat "$work/new" >>"$work/list"
	echo "findbig ${version}:"
	cat "$work/new"

	branch="chore/py-findbig-${version}"
	base=$(gh api "repos/${PACKAGES_REPO}/git/ref/heads/main" --jq .object.sha)
	gh api -X POST "repos/${PACKAGES_REPO}/git/refs" \
		-f "ref=refs/heads/${branch}" -f "sha=${base}" >/dev/null
	content=$(base64 <"$work/list" | tr -d '\n')
	gh api -X PUT "repos/${PACKAGES_REPO}/contents/${LIST_PATH}" \
		-f "message=findbig ${version}" -f "content=${content}" \
		-f "sha=${blob}" -f "branch=${branch}" >/dev/null
	gh pr create --repo "$PACKAGES_REPO" --base main --head "$branch" \
		--title "findbig ${version}" \
		--body "Adds py-findbig ${tag}'s .deb, .rpm, and .apk to ${LIST_PATH}, with the release candidate tag ${rc} their attestations name. Opened by the ${tag} release workflow."
}

[ $# -ge 1 ] || usage
command=$1
shift
case "$command" in
lines) lines "$@" ;;
pr) pr "$@" ;;
*) usage ;;
esac
