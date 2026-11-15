#!/bin/sh
# Point the Homebrew tap's findbig formula at a release.
#
# rewrite replaces the url and sha256 lines of a formula file in place, and
# refuses a file without exactly one of each or a checksum that is not 64
# lowercase hexadecimal digits. pr downloads the tag's source archive,
# rewrites a copy of the tap's Formula/findbig.rb, commits it to a new
# branch of the tap through the GitHub API, and opens a pull request; it
# needs gh with a token that may write the tap's contents and pull
# requests, and GITHUB_REPOSITORY (owner/py-findbig). It exits 0 without a
# change when the formula already names the archive.
#
# Exits 0 on success, 1 when a step fails, and 2 on a usage error.
#
# Usage: scripts/update-homebrew-formula.sh rewrite FORMULA URL SHA256
#        scripts/update-homebrew-formula.sh pr TAG
set -eu

TAP_REPO=${TAP_REPO:-cdf-eagles/homebrew-tap}
FORMULA_PATH=Formula/findbig.rb

usage() {
	echo "usage: update-homebrew-formula.sh rewrite FORMULA URL SHA256" >&2
	echo "       update-homebrew-formula.sh pr TAG" >&2
	exit 2
}

rewrite() {
	[ $# -eq 3 ] || usage
	file=$1
	url=$2
	sum=$3
	case "$sum" in
	*[!0-9a-f]* | "")
		echo "not a SHA-256 checksum: $sum" >&2
		exit 2
		;;
	*) ;;
	esac
	if [ "${#sum}" -ne 64 ]; then
		echo "not a SHA-256 checksum: $sum" >&2
		exit 2
	fi
	case "$url" in
	https://*) ;;
	*)
		echo "not an https URL: $url" >&2
		exit 2
		;;
	esac
	case "$url" in
	*'|'* | *'"'* | *\\* | *'&'*)
		echo "unsupported character in URL: $url" >&2
		exit 2
		;;
	*) ;;
	esac
	[ -f "$file" ] || {
		echo "no formula file: $file" >&2
		exit 2
	}
	for key in url sha256; do
		n=$(grep -c "^  ${key} \"" "$file" || true)
		if [ "$n" -ne 1 ]; then
			echo "expected one ${key} line in $file, found $n" >&2
			exit 2
		fi
	done
	tmp="${file}.tmp.$$"
	sed -e "s|^  url \".*\"\$|  url \"${url}\"|" \
		-e "s|^  sha256 \".*\"\$|  sha256 \"${sum}\"|" "$file" >"$tmp"
	mv "$tmp" "$file"
}

pr() {
	[ $# -eq 1 ] || usage
	tag=$1
	case "$tag" in
	v[0-9]*.[0-9]*.[0-9]*) ;;
	*)
		echo "unsupported tag $tag" >&2
		exit 2
		;;
	esac
	case "$tag" in
	*[!v0-9.]*)
		echo "unsupported tag $tag" >&2
		exit 2
		;;
	*) ;;
	esac
	repo=${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is not set}
	version=${tag#v}
	url="https://github.com/${repo}/archive/refs/tags/${tag}.tar.gz"
	work=$(mktemp -d)
	trap 'rm -rf "$work"' EXIT

	curl --proto "=https" --tlsv1.2 -sSfL -o "$work/source.tar.gz" "$url"
	if command -v sha256sum >/dev/null 2>&1; then
		sum=$(sha256sum "$work/source.tar.gz" | cut -d ' ' -f 1)
	else
		sum=$(shasum -a 256 "$work/source.tar.gz" | cut -d ' ' -f 1)
	fi

	gh api -H "Accept: application/vnd.github.raw+json" \
		"repos/${TAP_REPO}/contents/${FORMULA_PATH}" >"$work/findbig.rb"
	blob=$(gh api "repos/${TAP_REPO}/contents/${FORMULA_PATH}" --jq .sha)
	cp "$work/findbig.rb" "$work/before.rb"
	rewrite "$work/findbig.rb" "$url" "$sum"
	if cmp -s "$work/before.rb" "$work/findbig.rb"; then
		echo "${TAP_REPO} ${FORMULA_PATH} already names ${url}; nothing to do"
		return 0
	fi
	echo "findbig ${version}: ${url} sha256 ${sum}"

	branch="chore/findbig-${version}"
	base=$(gh api "repos/${TAP_REPO}/git/ref/heads/main" --jq .object.sha)
	gh api -X POST "repos/${TAP_REPO}/git/refs" \
		-f "ref=refs/heads/${branch}" -f "sha=${base}" >/dev/null
	content=$(base64 <"$work/findbig.rb" | tr -d '\n')
	gh api -X PUT "repos/${TAP_REPO}/contents/${FORMULA_PATH}" \
		-f "message=findbig ${version}" -f "content=${content}" \
		-f "sha=${blob}" -f "branch=${branch}" >/dev/null
	gh pr create --repo "$TAP_REPO" --base main --head "$branch" \
		--title "findbig ${version}" \
		--body "Points the findbig formula at py-findbig ${tag}: the url and sha256 of the release's source archive. Opened by the ${tag} release workflow of ${repo}."
}

[ $# -ge 1 ] || usage
command=$1
shift
case "$command" in
rewrite) rewrite "$@" ;;
pr) pr "$@" ;;
*) usage ;;
esac
