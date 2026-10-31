%global forgeurl https://github.com/storytold/pdfcraft
%global app_id   ai.storyteller.pdfcraft

# Rust release builds carry no debug info by default, so an empty debuginfo
# subpackage would fail the build. Skip it.
%global debug_package %{nil}

Name:           pdfcraft
Version:        0.16.1
Release:        1%{?dist}
Summary:        Open-source native PDF workbench

License:        MIT OR Apache-2.0
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/v%{version}/%{name}-%{version}.tar.gz

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
# mirror upstream's packaging/linux/nfpm.yaml. Printing shells out to CUPS's
# lpstat/lp; without it the Print dialog still offers Save as PDF.
Requires:       libxkbcommon.so.0()(64bit)
Requires:       (libvulkan.so.1()(64bit) or libEGL.so.1()(64bit))
Recommends:     cups-client
Recommends:     libwayland-client.so.0()(64bit)
Recommends:     libX11.so.6()(64bit)
Recommends:     libX11-xcb.so.1()(64bit)
Recommends:     libXcursor.so.1()(64bit)
Recommends:     libXi.so.6()(64bit)
Recommends:     libXrandr.so.2()(64bit)
Recommends:     mesa-vulkan-drivers
Recommends:     xdg-desktop-portal
# Scan & OCR needs these; upstream looks in <bindir>/../share/pdfcraft/models,
# which is where pdfcraft-ocr-models installs them.
Recommends:     pdfcraft-ocr-models

ExclusiveArch:  x86_64 aarch64

%description
PdfCraft is an open-source, native PDF workbench: read, comment, fill and
sign forms, organize, combine, split, edit, redact, protect and export PDFs.

Includes pdfcraft-cli, a headless command runner and opt-in MCP server.

This build does not embed the optional craft-fonts set (Japanese UI/type
fallback); system fonts are used instead. Text recognition (Scan & OCR)
needs the pdfcraft-ocr-models package.

%prep
%autosetup -n %{name}-%{version}

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
* Sat Oct 31 2026 Dexxiez <toby@boulton.net.au> - 0.16.1-1
- Update to 0.16.1

* Thu Oct 29 2026 Dexxiez <toby@boulton.net.au> - 0.15.0-1
- Update to 0.15.0

* Sun Oct 25 2026 Dexxiez <toby@boulton.net.au> - 0.14.0-1
- Update to 0.14.0

* Fri Oct 23 2026 Dexxiez <toby@boulton.net.au> - 0.13.0-1
- Update to 0.13.0

* Wed Oct 21 2026 Dexxiez <toby@boulton.net.au> - 0.10.1-1
- Update to 0.10.1

* Sun Oct 18 2026 Dexxiez <toby@boulton.net.au> - 0.9.0-1
- Update to 0.9.0

* Thu Oct 15 2026 Dexxiez <toby@boulton.net.au> - 0.8.0-1
- Update to 0.8.0

* Tue Oct 13 2026 Dexxiez <toby@boulton.net.au> - 0.7.1-1
- Update to 0.7.1

* Mon Oct 12 2026 Dexxiez <toby@boulton.net.au> - 0.6.0-1
- Update to 0.6.0, track tagged releases instead of main
- Drop system models dir patch, upstream now searches ../share/pdfcraft/models
- Recommend cups-client for printing

* Sun Oct 11 2026 Dexxiez <toby@boulton.net.au> - 0.2.1^20261011gitbbbe600-1
- Update to 0.2.1^20261011gitbbbe600

* Sat Oct 10 2026 Dexxiez <toby@boulton.net.au> - 0.2.1^20261010git5d59060-1
- Update to 0.2.1^20261010git5d59060

* Fri Oct 09 2026 Dexxiez <toby@boulton.net.au> - 0.2.1^20261009git653f826-1
- Update to 0.2.1^20261009git653f826

* Thu Oct 08 2026 Dexxiez <toby@boulton.net.au> - 0.2.1^20261008git1b62d47-1
- Update to 0.2.1^20261008git1b62d47

* Thu Oct 08 2026 Dexxiez <toby@boulton.net.au> - 0.2.1^20261008git6974c65-2
- Look for OCR models in /usr/share/pdfcraft/models
- Recommend pdfcraft-ocr-models

* Thu Oct 08 2026 Dexxiez <toby@boulton.net.au> - 0.2.1^20261008git6974c65-1
- Initial package, snapshot of main
