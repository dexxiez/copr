#!/usr/bin/env bash
# Build a source RPM for one package directory.
#   usage: scripts/build_srpm.sh <package-name> [output-dir]
# Prints the path of the resulting .src.rpm on stdout (last line).
set -euo pipefail

PKG="${1:?usage: build_srpm.sh <package-name> [output-dir]}"
OUTDIR="${2:-$PWD/srpms}"
SPEC="packages/${PKG}/${PKG}.spec"

[[ -f "$SPEC" ]] || { echo "no spec at $SPEC" >&2; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK"/{SOURCES,SPECS,SRPMS} "$OUTDIR"

# Copy the spec plus any patches / extra sources sitting next to it
cp "$SPEC" "$WORK/SPECS/"
find "packages/${PKG}" -maxdepth 1 -type f \
     ! -name '*.spec' ! -name 'package.yaml' \
     -exec cp {} "$WORK/SOURCES/" \;

# Download Source0 etc. from upstream
spectool -g -R --define "_topdir $WORK" "$WORK/SPECS/${PKG}.spec"

rpmbuild -bs --define "_topdir $WORK" "$WORK/SPECS/${PKG}.spec"

SRPM="$(find "$WORK/SRPMS" -name '*.src.rpm' | head -n1)"
cp "$SRPM" "$OUTDIR/"
echo "$OUTDIR/$(basename "$SRPM")"
