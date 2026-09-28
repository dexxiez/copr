#!/usr/bin/env python3
"""Check each package against its upstream GitHub releases or git branch.

For packages with `auto: true`, bump the spec (Version, Release, %changelog).
For packages with `auto: false`, just report that a new version exists.

Packages with `git` + `branch` in package.yaml track the branch head instead
of releases. Their spec carries `%global commit <sha>` and a snapshot
`Version: <base>^<YYYYMMDD>git<shortsha>`; a new head rewrites both.

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
import subprocess
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


def branch_head(url: str, branch: str) -> str | None:
    """Return the commit SHA at the tip of `branch`, via `git ls-remote`."""
    try:
        out = subprocess.run(
            ["git", "ls-remote", url, f"refs/heads/{branch}"],
            capture_output=True, text=True, check=True, timeout=60,
        ).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"  ! git ls-remote failed for {url}: {e}", file=sys.stderr)
        return None
    return out.split()[0] if out.strip() else None


def spec_commit(text: str) -> str | None:
    m = re.search(r"^%global\s+commit\s+(\S+)\s*$", text, re.M)
    return m.group(1) if m else None


def check_branch(meta: dict, text: str, current: str) -> tuple[str, str] | None:
    """Return (new_version, new_commit) if the branch head moved, else None.

    The snapshot date is the day of the check, not the commit date, so it
    stays monotonic without needing a forge-specific API.
    """
    name, url, branch = meta["name"], meta["git"], meta.get("branch", "main")
    head = branch_head(url, branch)
    if not head:
        return None
    if head == spec_commit(text):
        print(f"{name}: up to date ({branch} @ {head[:7]})", file=sys.stderr)
        return None
    base = current.split("^", 1)[0]
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"{base}^{date}git{head[:7]}", head


def set_commit(text: str, commit: str) -> str:
    return re.sub(r"^(%global\s+commit\s+)\S+", rf"\g<1>{commit}", text, count=1, flags=re.M)


def check_releases(meta: dict, current: str) -> str | None:
    """Return the newest eligible release version if newer than `current`."""
    name = meta["name"]
    tags = release_tags(meta["upstream"], meta.get("skip_prerelease", True))
    if not tags:
        return None

    prefix = meta.get("tag_prefix", "v") or ""
    versions = [
        t[len(prefix):] if prefix and t.startswith(prefix) else t
        for t in tags
    ]
    versions = [v for v in versions if is_version(v)]
    if not versions:
        print(f"{name}: no version-like release tags", file=sys.stderr)
        return None

    # `pin` is an fnmatch pattern against the upstream version. "18.20.1"
    # holds the package at exactly that release; "18.20.*" follows the
    # 18.20 series only; unset (or "*") tracks the newest release.
    pin = str(meta.get("pin", "*") or "*")
    allowed = [v for v in versions if fnmatch.fnmatch(v, pin)]
    if not allowed:
        print(f"{name}: no release matches pin '{pin}'", file=sys.stderr)
        return None

    upstream_version = max(allowed, key=vkey)

    if not newer(upstream_version, current):
        pinned = " (pinned to '%s')" % pin if pin != "*" else ""
        print(f"{name}: up to date ({current}){pinned}", file=sys.stderr)
        return None

    return upstream_version


def main() -> int:
    bumped, notices = [], []

    for meta_file in sorted(PACKAGES.glob("*/package.yaml")):
        meta = yaml.safe_load(meta_file.read_text()) or {}
        name = meta.setdefault("name", meta_file.parent.name)
        if not meta.get("upstream") and not meta.get("git"):
            print(f"{name}: no upstream or git set, skipping", file=sys.stderr)
            continue

        spec_path = meta_file.parent / f"{name}.spec"
        if not spec_path.exists():
            print(f"{name}: no spec file, skipping", file=sys.stderr)
            continue

        text = spec_path.read_text()
        current = spec_version(text)
        if not current:
            continue

        if meta.get("git"):
            found = check_branch(meta, text, current)
        else:
            version = check_releases(meta, current)
            found = (version, None) if version else None
        if not found:
            continue
        new_version, commit = found

        record = {"name": name, "old": current, "new": new_version}
        if meta.get("auto", False):
            new_text = bump(text, new_version)
            if commit:
                new_text = set_commit(new_text, commit)
            spec_path.write_text(new_text)
            bumped.append(record)
            print(f"{name}: bumped {current} -> {new_version}", file=sys.stderr)
        else:
            notices.append(record)
            print(f"{name}: update available {current} -> {new_version} (manual)", file=sys.stderr)

    json.dump({"bumped": bumped, "notices": notices}, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
