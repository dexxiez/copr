# copr-builds

RPM spec files and automation for my [COPR](https://copr.fedorainfracloud.org/) repo.

Each package lives in `packages/<name>/` with a `.spec` file and a `package.yaml`
describing where upstream lives. A daily job checks GitHub releases; packages
marked `auto: true` get bumped and rebuilt on their own, the rest just raise an
issue so I can do it by hand.

## Layout

```
packages/<name>/<name>.spec     the spec file
packages/<name>/package.yaml    upstream repo + auto/manual flag
packages/<name>/*.patch         any extra sources, copied into SOURCES
scripts/build_srpm.sh           spec -> .src.rpm (used locally and in CI)
scripts/check_updates.py        release checker / spec bumper
.github/workflows/copr-build.yml     builds + submits to COPR
.github/workflows/check-updates.yml  daily upstream check
```

## One-time setup

1. **Make an API token.** Go to <https://copr.fedorainfracloud.org/api/> and copy
   the whole config block it shows you.
2. **Add it as a secret.** Repo → Settings → Secrets and variables → Actions →
   *Secrets* → New secret, named `COPR_CONFIG`, paste the block in.
3. **Add two variables** on the *Variables* tab of the same page:
   - `COPR_PROJECT` — e.g. `yourusername/yourproject`
   - `PACKAGER` — e.g. `Your Name <you@example.com>` (goes in `%changelog`)
4. Repo → Settings → Actions → General → Workflow permissions →
   **Read and write permissions**. The update job needs this to push bumps.

## Adding a package

```bash
mkdir -p packages/foo
cp packages/atuin/package.yaml packages/foo/
$EDITOR packages/foo/package.yaml     # name, upstream, auto
$EDITOR packages/foo/foo.spec         # start from atuin.spec
```

Test the SRPM locally before pushing (needs `rpmdevtools` and `rpm-build`):

```bash
./scripts/build_srpm.sh foo
```

Push to `main` and only the packages you touched get rebuilt.

## Pinning a version

Add a `pin` to a package's `package.yaml`. It's a glob matched against the
upstream version number:

```yaml
pin: "18.20.1"   # stay on exactly this release
pin: "18.20.*"   # follow the 18.20 series, never move to 18.21
pin: "18.*"      # stay on the 18.x major
```

Leave it out to track the newest release. A pin still lets the checker move
*up* to the pin — if the spec says 18.20.1 and you pin `18.20.2`, it bumps once
and then holds. To unpin, delete the line.

Note that `pin` and `auto` are independent: a pinned package with `auto: true`
will still build automatically, just only within the pinned range.

## Manual builds

Actions → **COPR build** → Run workflow → type a package name, a comma-separated
list, or `all`.

## Notes

- Builds are submitted as SRPMs, so the chroots (Fedora versions, architectures)
  are whatever you've enabled in the COPR project's own settings.
- `Source0` uses `%{version}`, so bumping `Version:` is all that's needed for
  most GitHub projects. Projects that publish a release *asset* tarball rather
  than the auto-generated one need a different `Source0` URL.
- The version comparison in `check_updates.py` is a simple numeric-chunk sort.
  Projects with odd tagging (dates, `release-` prefixes) may need `tag_prefix`
  set or a tweak.
