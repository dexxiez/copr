#!/usr/bin/env python3
"""Check each package against its upstream GitHub releases.

For packages with `auto: true`, bump the spec (Version, Release, %changelog).
For packages with `auto: false`, just report that a new version exists.

Outputs JSON to stdout:
  {"bumped": [{"name":..., "old":..., "new":...}],
   "notices": [{"name":..., "old":..., "new":...}]}

Env:
  GITHUB_TOKEN   optional, avoids API rate limits
  PACKAGER       e.g. "Your Name <you@example.com>", used in %changelog
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "packages"
PACKAGER = os.environ.get("PACKAGER", "Automated Build <builds@example.com>")
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def api(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def release_tags(repo: str, skip_prerelease: bool = True) -> list[str]:
    """Return recent release tags, newest first."""
    try:
        releases = api(f"https://api.github.com/repos/{repo}/releases?per_page=100")
    except urllib.error.HTTPError as e:
        print(f"  ! GitHub API error for {repo}: {e}", file=sys.stderr)
        return []
    tags = []
    for rel in releases:
        if rel.get("draft"):
            continue
        if skip_prerelease and rel.get("prerelease"):
            continue
        tags.append(rel["tag_name"])
    return tags


# A tag we are willing to treat as a version: starts with a digit, then only
# digits, dots, dashes, underscores and word characters. Rules out upstream
# aliases and asset tags like "stable", "cn-base" or "MapleX".
VERSION_TAG = re.compile(r"^\d[\w._-]*$")


def is_version(v: str) -> bool:
    return bool(VERSION_TAG.match(v))


def vkey(v: str):
    """Rough version sort key: split into numeric and text chunks.

    Each chunk becomes a (rank, number, text) tuple so numeric and textual
    chunks stay mutually comparable — numbers sort before text, so "1.2"
    beats "1.2rc1".
    """
    key = []
    for p in re.split(r"[._-]", v):
        key.append((0, int(p), "") if p.isdigit() else (1, 0, p))
    return key


def newer(new: str, old: str) -> bool:
    return vkey(new) > vkey(old)


def spec_version(text: str) -> str | None:
    m = re.search(r"^Version:\s*(\S+)\s*$", text, re.M)
    return m.group(1) if m else None


def bump(text: str, new: str) -> str:
    text = re.sub(r"^Version:(\s*)\S+\s*$", rf"Version:\g<1>{new}", text, count=1, flags=re.M)
    text = re.sub(r"^Release:(\s*)\S+.*$", r"Release:\g<1>1%{?dist}", text, count=1, flags=re.M)
    date = datetime.now(timezone.utc).strftime("%a %b %d %Y")
    entry = f"* {date} {PACKAGER} - {new}-1\n- Update to {new}\n"
    return re.sub(r"^%changelog\s*\n", f"%changelog\n{entry}\n", text, count=1, flags=re.M)


def main() -> int:
    bumped, notices = [], []

    for meta_file in sorted(PACKAGES.glob("*/package.yaml")):
        meta = yaml.safe_load(meta_file.read_text()) or {}
        name = meta.get("name", meta_file.parent.name)
        upstream = meta.get("upstream")
        if not upstream:
            print(f"{name}: no upstream set, skipping", file=sys.stderr)
            continue

        spec_path = meta_file.parent / f"{name}.spec"
        if not spec_path.exists():
            print(f"{name}: no spec file, skipping", file=sys.stderr)
            continue

        text = spec_path.read_text()
        current = spec_version(text)
        if not current:
            continue

        tags = release_tags(upstream, meta.get("skip_prerelease", True))
        if not tags:
            continue

        prefix = meta.get("tag_prefix", "v") or ""
        versions = [
            t[len(prefix):] if prefix and t.startswith(prefix) else t
            for t in tags
        ]
        versions = [v for v in versions if is_version(v)]
        if not versions:
            print(f"{name}: no version-like release tags", file=sys.stderr)
            continue

        # `pin` is an fnmatch pattern against the upstream version. "18.20.1"
        # holds the package at exactly that release; "18.20.*" follows the
        # 18.20 series only; unset (or "*") tracks the newest release.
        pin = str(meta.get("pin", "*") or "*")
        allowed = [v for v in versions if fnmatch.fnmatch(v, pin)]
        if not allowed:
            print(f"{name}: no release matches pin '{pin}'", file=sys.stderr)
            continue

        upstream_version = max(allowed, key=vkey)

        if not newer(upstream_version, current):
            pinned = " (pinned to '%s')" % pin if pin != "*" else ""
            print(f"{name}: up to date ({current}){pinned}", file=sys.stderr)
            continue

        record = {"name": name, "old": current, "new": upstream_version}
        if meta.get("auto", False):
            spec_path.write_text(bump(text, upstream_version))
            bumped.append(record)
            print(f"{name}: bumped {current} -> {upstream_version}", file=sys.stderr)
        else:
            notices.append(record)
            print(f"{name}: update available {current} -> {upstream_version} (manual)", file=sys.stderr)

    json.dump({"bumped": bumped, "notices": notices}, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
