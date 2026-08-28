# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

RPM spec files + automation for a personal COPR repo. No application code — the "product" is `.spec`/`package.yaml` pairs plus two scripts and two GitHub Actions workflows that build and auto-update them.

## Layout

```
packages/<name>/<name>.spec     the spec file
packages/<name>/package.yaml    upstream repo + auto/manual flag
packages/<name>/*.patch         any extra sources, copied into SOURCES
scripts/build_srpm.sh           spec -> .src.rpm (used locally and in CI)
scripts/check_updates.py        release checker / spec bumper
srpms/                          local build output (gitignored-style, not source of truth)
.github/workflows/copr-build.yml     builds + submits to COPR
.github/workflows/check-updates.yml  daily upstream check
```

## Commands

Build a package's SRPM locally (needs `rpmdevtools` and `rpm-build`):

```bash
./scripts/build_srpm.sh <package-name> [output-dir]   # defaults to ./srpms
```

Run the upstream update checker locally (needs `pyyaml`; set `PACKAGER` and optionally `GITHUB_TOKEN`):

```bash
PACKAGER="Name <email>" python scripts/check_updates.py
```

There is no test suite, linter, or build step beyond the above — `build_srpm.sh` succeeding is the correctness check for a spec.

## Adding a package

```bash
mkdir -p packages/foo
cp packages/atuin/package.yaml packages/foo/
$EDITOR packages/foo/package.yaml     # name, upstream, auto
$EDITOR packages/foo/foo.spec         # start from an existing spec, e.g. atuin.spec
./scripts/build_srpm.sh foo           # verify before pushing
```

Push to `main`; only packages whose files changed under `packages/` get rebuilt (`copr-build.yml`'s `prepare` job diffs `packages/` between the push's before/after SHAs).

## `package.yaml` fields

- `name` — must match the directory and `<name>.spec`.
- `upstream` — `owner/repo` on GitHub; releases are read via the GitHub API.
- `auto` — `true`: `check_updates.py` bumps `Version:`/`Release:`/`%changelog` in the spec automatically and commits. `false`: only opens/reuses a GitHub issue titled `<name>: upstream released <version>`.
- `tag_prefix` — stripped from release tags before comparing (default `"v"`).
- `skip_prerelease` — default `true`.
- `pin` — an `fnmatch` glob against the upstream version (e.g. `"18.20.1"`, `"18.20.*"`, `"18.*"`). Restricts which releases are eligible; the checker still bumps *within* the pinned range. Independent of `auto`.

## Spec file conventions

- `Source0` should use `%{version}` so bumping `Version:` is sufficient for standard GitHub-generated tarballs. Packages using a release *asset* tarball need a hand-maintained `Source0` URL instead — `check_updates.py` never touches `Source0`.
- Version comparisons in `check_updates.py` are a naive numeric-chunk split-and-compare (`vkey`/`newer`). Packages with unusual tags (dates, `release-` prefixes) need `tag_prefix` set or the comparison will misbehave.

## CI/CD architecture

- `check-updates.yml` runs daily, calls `check_updates.py`, commits any auto-bumped specs directly to `main` as `github-actions[bot]`, opens GitHub issues for manual-update packages (dedup'd by title search), then invokes `copr-build.yml` (via `workflow_call`) for whatever it bumped.
- `copr-build.yml` also runs directly on push-to-main (path-filtered to `packages/**`) and via manual `workflow_dispatch` (comma-separated names or `all`). Each selected package builds in its own `fedora:latest` container matrix job: SRPM via `build_srpm.sh`, then `copr-cli build --nowait` against `vars.COPR_PROJECT` using the `secrets.COPR_CONFIG` file dropped at `~/.config/copr`.
- Chroots/architectures are controlled entirely by the COPR project's own settings, not by anything in this repo — builds are submitted as SRPMs only.

## Repo secrets/vars required (see README for setup)

- Secret `COPR_CONFIG` — full API token block from the COPR web UI.
- Variable `COPR_PROJECT` — e.g. `username/project`.
- Variable `PACKAGER` — used in `%changelog` entries.
- Actions workflow permissions must be "Read and write" for the daily job to push bumps.
