%global forgeurl https://github.com/storytold/wordcraft
%global app_id   ai.storyteller.wordcraft

# Rust release builds carry no debug info by default, so an empty debuginfo
# subpackage would fail the build. Skip it.
%global debug_package %{nil}

Name:           wordcraft
Version:        0.12.0
Release:        1%{?dist}
Summary:        Open-source native word processor

License:        MIT OR Apache-2.0
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  rust >= 1.95
BuildRequires:  cargo
# a few crates compile small C helpers via the cc crate
BuildRequires:  gcc
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
WordCraft is an open-source, native word processor that works the way Word
users expect: the ribbon, styles, tables, track changes, references and mail
merge. It reads and writes .docx, opens .odt, .rtf, .html, .md and .txt, and
exports PDF.

Includes wordcraft-cli, a headless converter and command runner.

This build does not embed the optional craft-fonts set (Japanese UI/type
fallback); system fonts are used instead.

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
cargo build --release --locked --package %{name} --package %{name}-cli

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
* Thu Oct 29 2026 Dexxiez <toby@boulton.net.au> - 0.12.0-1
- Update to 0.12.0

* Sun Oct 25 2026 Dexxiez <toby@boulton.net.au> - 0.11.0-1
- Update to 0.11.0

* Fri Oct 23 2026 Dexxiez <toby@boulton.net.au> - 0.10.0-1
- Update to 0.10.0

* Wed Oct 21 2026 Dexxiez <toby@boulton.net.au> - 0.9.0-1
- Update to 0.9.0

* Tue Oct 20 2026 Dexxiez <toby@boulton.net.au> - 0.8.0-1
- Initial package
