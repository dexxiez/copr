# Source tarball signing key, from upstream's PACKAGING.md.
%global ghostty_pubkey RWQlAjJC23149WL2sEpT/l0QKy7hMIFhYdQOFy0Z7z7PbneUgvlsnYcV
%global appid com.mitchellh.ghostty

# Ghostty needs the exact Zig minor in build.zig.zon (minimum_zig_version).
# Fedora ships 0.16 but 1.4 needs 0.17, so the official Zig toolchain is
# bundled as a build-only source. Key from https://ziglang.org/download/.
%global zig_version 0.17.1
%global zig_pubkey RWSGOq2NVecA2UPNdBUZykf1CCb147pkmdtYxgb3Ti+JO/wCYvhbAb/U
%global zig_dist https://ziglang.org/download/%{zig_version}

# Built with -Dstrip, so an empty debuginfo subpackage would fail.
%global debug_package %{nil}

Name:           ghostty
Version:        1.4.0
Release:        1%{?dist}
Summary:        Fast, feature-rich, GPU-accelerated terminal emulator

# Ghostty is MIT; bundled deps and fonts bring in the rest.
License:        MIT AND MPL-2.0 AND OFL-1.1 AND (WTFPL OR CC0-1.0) AND Apache-2.0
URL:            https://ghostty.org
# Use the release tarball, not a git archive: it carries pre-generated files.
Source0:        https://release.files.ghostty.org/%{version}/%{name}-%{version}.tar.gz
Source1:        https://release.files.ghostty.org/%{version}/%{name}-%{version}.tar.gz.minisig
Source10:       %{zig_dist}/zig-x86_64-linux-%{zig_version}.tar.xz
Source11:       %{zig_dist}/zig-x86_64-linux-%{zig_version}.tar.xz.minisig
Source12:       %{zig_dist}/zig-aarch64-linux-%{zig_version}.tar.xz
Source13:       %{zig_dist}/zig-aarch64-linux-%{zig_version}.tar.xz.minisig

BuildRequires:  minisign
BuildRequires:  gettext
BuildRequires:  pandoc-cli
BuildRequires:  ncurses
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(libadwaita-1)
BuildRequires:  pkgconfig(gtk4-layer-shell-0)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(egl)

# Fedora's ncurses-term ships terminfo/g/ghostty; we only add xterm-ghostty.
Requires:       ncurses-term

ExclusiveArch:  x86_64 aarch64
%ifarch x86_64
%global zig_src %{SOURCE10}
%global zig_sig %{SOURCE11}
%endif
%ifarch aarch64
%global zig_src %{SOURCE12}
%global zig_sig %{SOURCE13}
%endif

%description
Ghostty is a fast, feature-rich, cross-platform terminal emulator that uses
platform-native UI and GPU acceleration.

%prep
minisign -V -P '%{ghostty_pubkey}' -m '%{SOURCE0}' -x '%{SOURCE1}'
minisign -V -P '%{zig_pubkey}' -m '%{zig_src}' -x '%{zig_sig}'
%autosetup
mkdir -p .zig
tar -xf '%{zig_src}' -C .zig --strip-components=1

%build
# Zig package dependencies (build.zig.zon) are fetched from
# deps.files.ghostty.org here, so COPR builds need networking enabled.
export ZIG_GLOBAL_CACHE_DIR="%{_builddir}/.cache/zig"
DESTDIR="%{_builddir}/destdir" ./.zig/zig build install \
    -j%{_smp_build_ncpus} \
    --prefix %{_prefix} \
    -Doptimize=ReleaseFast \
    -Dcpu=baseline \
    -Dpie=true \
    -Dstrip=true \
    -Demit-docs \
    -Dinstalled-exe-path=%{_bindir}/%{name} \
    -Dversion-string=%{version}

%install
mkdir -p %{buildroot}
cp -a %{_builddir}/destdir/. %{buildroot}/
# libghostty-vt is built alongside the app (into /usr/lib, not %%{_libdir}).
# Nothing here needs it, and its .a trips brp-strip, so don't ship it.
rm -rf %{buildroot}%{_prefix}/lib/libghostty-vt.* \
       %{buildroot}%{_includedir}/ghostty \
       %{buildroot}%{_datadir}/pkgconfig/libghostty-vt*.pc
# Already provided by ncurses-term.
rm -f %{buildroot}%{_datadir}/terminfo/g/%{name}
%find_lang %{appid}

%check
%{buildroot}%{_bindir}/%{name} +version

%post
%systemd_user_post app-%{appid}.service

%preun
%systemd_user_preun app-%{appid}.service

%files -f %{appid}.lang
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/metainfo/%{appid}.metainfo.xml
%{_datadir}/dbus-1/services/%{appid}.service
%{_datadir}/systemd/user/app-%{appid}.service
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
%{_datadir}/terminfo/x/xterm-%{name}
%{_mandir}/man1/%{name}.1*
%{_mandir}/man5/%{name}.5*
%{_datadir}/bash-completion/completions/%{name}.bash
%{_datadir}/fish/vendor_completions.d/%{name}.fish
%{_datadir}/zsh/site-functions/_%{name}
%{_datadir}/bat/syntaxes/%{name}.sublime-syntax
%{_datadir}/vim/vimfiles/*/%{name}.vim
%{_datadir}/nvim/site/*/%{name}.vim
%{_datadir}/kio/servicemenus/%{appid}.desktop
%{_datadir}/nautilus-python/extensions/%{name}.py

%changelog
* Fri Nov 20 2026 Dexxiez <toby@boulton.net.au> - 1.4.0-1
- Initial package
