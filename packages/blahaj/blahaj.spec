%global forgeurl https://codeberg.org/GeopJr/BLAHAJ

# Snapshot of the main branch. check_updates.py rewrites `commit` and the
# snapshot suffix of Version together; the base (before `^`) is bumped by hand.
%global commit 9651b5ee47e2d930f400cac31eabf39691c1150a
%global shortcommit %(c=%{commit}; echo ${c:0:7})

# Built with --no-debug, so an empty debuginfo subpackage would fail.
%global debug_package %{nil}

# Fedora does not package Crystal, so the official bundled toolchain (which
# ships its own libgc and libpcre2) is fetched below. shard.yml declares
# crystal >= 1.8.0. When bumping, update the version and both checksums from
# https://github.com/crystal-lang/crystal/releases
%global crystal_version 1.21.1
%ifarch x86_64
%global crystal_sha256 391dff4244d8d11c4422def9a2f930c9ba9fc9b7c85a20cbcc494472ab77bc0e
%endif
%ifarch aarch64
%global crystal_sha256 06e1408c6d759b6132a318ae65c6aecd070a9c3e6c8cc5d916cf25fd07cea8ef
%endif

Name:           blahaj
Version:        2.2.0^20260501git9651b5e
Release:        1%{?dist}
Summary:        Gay sharks at your local terminal - lolcat-like CLI tool

License:        BSD-2-Clause
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/%{commit}.tar.gz#/%{name}-%{shortcommit}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  curl
BuildRequires:  tar
BuildRequires:  gzip
BuildRequires:  ca-certificates
# Crystal's stdlib links these from the system; std YAML needs libyaml.
BuildRequires:  libyaml-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel

# Official Crystal Linux tarballs exist only for these.
ExclusiveArch:  x86_64 aarch64

%description
BLAHAJ is a lolcat-like CLI tool that colorizes its input using pride flag
color palettes. It can also print the flags themselves and the BLAHAJ shark
ASCII art.

%prep
# Codeberg archives unpack into the lowercased repository name.
%autosetup -n %{name}

%build
CRYSTAL_DIST="crystal-%{crystal_version}-1"
CRYSTAL_TARBALL="${CRYSTAL_DIST}-linux-%{_arch}-bundled.tar.gz"
curl -sSfL --retry 3 -o "$CRYSTAL_TARBALL" \
  "https://github.com/crystal-lang/crystal/releases/download/%{crystal_version}/${CRYSTAL_TARBALL}"
echo "%{crystal_sha256}  ${CRYSTAL_TARBALL}" | sha256sum -c -
tar xf "$CRYSTAL_TARBALL"
export PATH="$PWD/${CRYSTAL_DIST}/bin:$PATH"
crystal --version

export CRYSTAL_CACHE_DIR="%{_builddir}/.cache/crystal"
%make_build build

%install
%make_install PREFIX=%{_prefix}

%check
# No --version flag; colorizing stdin exercises the flag data and YAML parsing.
echo blahaj | bin/%{name} -c trans

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}

%changelog
* Mon Sep 28 2026 Dexxiez <toby@boulton.net.au> - 2.2.0^20260501git9651b5e-1
- Initial package, snapshot of main
