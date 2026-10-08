%global forgeurl https://github.com/storytold/pdfcraft
%global app_id   ai.storyteller.pdfcraft

# Snapshot of the main branch: upstream has not tagged a release since the
# printcraft -> pdfcraft rename. check_updates.py rewrites `commit` and the
# snapshot suffix of Version together; the base (before `^`) is bumped by hand.
%global commit 6974c6550d9dbcfdada41bc902c1aa16d3b72a0a
%global shortcommit %(c=%{commit}; echo ${c:0:7})

# Rust release builds carry no debug info by default, so an empty debuginfo
# subpackage would fail the build. Skip it.
%global debug_package %{nil}

Name:           pdfcraft
Version:        0.2.1^20261008git6974c65
Release:        1%{?dist}
Summary:        Open-source native PDF workbench

License:        MIT OR Apache-2.0
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/%{commit}.tar.gz#/%{name}-%{shortcommit}.tar.gz

BuildRequires:  rust >= 1.90
BuildRequires:  cargo
# aws-lc-sys (RSA signing) compiles C/C++ and may fall back to cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  appstream

# Windowing (X11/Wayland, xkbcommon) and the GPU (Vulkan, EGL) are loaded at
# runtime with dlopen, so rpm's dependency generator can't see them. These
# mirror upstream's packaging/linux/nfpm.yaml.
Requires:       libxkbcommon.so.0()(64bit)
Requires:       (libvulkan.so.1()(64bit) or libEGL.so.1()(64bit))
Recommends:     libwayland-client.so.0()(64bit)
Recommends:     libX11.so.6()(64bit)
Recommends:     libX11-xcb.so.1()(64bit)
Recommends:     libXcursor.so.1()(64bit)
Recommends:     libXi.so.6()(64bit)
Recommends:     libXrandr.so.2()(64bit)
Recommends:     mesa-vulkan-drivers
Recommends:     xdg-desktop-portal

ExclusiveArch:  x86_64 aarch64

%description
PdfCraft is an open-source, native PDF workbench: read, comment, fill and
sign forms, organize, combine, split, edit, redact, protect and export PDFs.

Includes pdfcraft-cli, a headless command runner and opt-in MCP server.

This build does not embed the optional craft-fonts set (Japanese UI/type
fallback); system fonts are used instead.

%prep
%autosetup -n %{name}-%{commit}

%build
# Fedora's %%cargo_build macro expects a rust2rpm-style vendored registry.
# This package fetches crates from the network during the build instead,
# which COPR's buildroots permit.
export CARGO_HOME="%{_builddir}/.cargo"
# Only set if the macro exists, so an older buildroot doesn't end up with a
# literal "%%{build_rustflags}" in RUSTFLAGS.
%{?build_rustflags:export RUSTFLAGS="%{build_rustflags}"}
cargo build --release --locked --package pdfcraft --package pdfcraft-cli

%install
install -Dpm0755 target/release/%{name}     %{buildroot}%{_bindir}/%{name}
install -Dpm0755 target/release/%{name}-cli %{buildroot}%{_bindir}/%{name}-cli

install -Dpm0644 packaging/linux/%{app_id}.desktop \
    %{buildroot}%{_datadir}/applications/%{app_id}.desktop
install -Dpm0644 packaging/linux/%{app_id}.mime.xml \
    %{buildroot}%{_datadir}/mime/packages/%{app_id}.xml

install -d %{buildroot}%{_metainfodir}
sed -e "s/@VERSION@/%{version}/g" -e "s/@DATE@/$(date -u +%%Y-%%m-%%d)/g" \
    packaging/linux/%{app_id}.metainfo.xml.in \
    > %{buildroot}%{_metainfodir}/%{app_id}.metainfo.xml

install -d %{buildroot}%{_datadir}/icons
cp -R assets/app-icon/hicolor %{buildroot}%{_datadir}/icons/

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{app_id}.desktop
appstreamcli validate --no-net %{buildroot}%{_metainfodir}/%{app_id}.metainfo.xml
target/release/%{name}-cli --version

%files
%license LICENSE-MIT LICENSE-APACHE NOTICE
%doc README.md
%{_bindir}/%{name}
%{_bindir}/%{name}-cli
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/mime/packages/%{app_id}.xml
%{_metainfodir}/%{app_id}.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/%{app_id}.*

%changelog
* Thu Oct 08 2026 Dexxiez <toby@boulton.net.au> - 0.2.1^20261008git6974c65-1
- Initial package, snapshot of main
