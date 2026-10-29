%global forgeurl https://github.com/storytold/figcraft
%global app_id   ai.storyteller.figcraft

# Rust release builds carry no debug info by default, so an empty debuginfo
# subpackage would fail the build. Skip it.
%global debug_package %{nil}

Name:           figcraft
Version:        0.12.1
Release:        1%{?dist}
Summary:        Open-source native interface design and prototyping tool

License:        MIT OR Apache-2.0
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  rust >= 1.95
BuildRequires:  cargo
# ring compiles small C/asm helpers via the cc crate
BuildRequires:  gcc
BuildRequires:  desktop-file-utils
BuildRequires:  appstream

# Windowing (X11/Wayland, xkbcommon) and the GPU (Vulkan, EGL) are loaded at
# runtime with dlopen, so rpm's dependency generator can't see them. These
# mirror upstream's packaging/linux/nfpm.yaml.
Requires:       libxkbcommon.so.0()(64bit)
Requires:       libxkbcommon-x11.so.0()(64bit)
Requires:       libwayland-client.so.0()(64bit)
Requires:       libX11.so.6()(64bit)
Requires:       libX11-xcb.so.1()(64bit)
Requires:       libxcb.so.1()(64bit)
Requires:       libXcursor.so.1()(64bit)
Requires:       libXi.so.6()(64bit)
Requires:       (libvulkan.so.1()(64bit) or libEGL.so.1()(64bit))
Recommends:     mesa-vulkan-drivers
Recommends:     xdg-desktop-portal

ExclusiveArch:  x86_64 aarch64

%description
FigCraft is an open-source, native interface design and prototyping tool:
frames, vector shapes and text on an infinite canvas; auto layout and
constraints; components, variants, styles and variables; interactive
prototypes with a presentation mode; SVG and PNG export; GPU rendering (wgpu).

Includes figcraft-cli, a headless command runner and MCP server.

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
* Thu Oct 29 2026 Dexxiez <toby@boulton.net.au> - 0.12.1-1
- Update to 0.12.1

* Sun Oct 25 2026 Dexxiez <toby@boulton.net.au> - 0.11.2-1
- Update to 0.11.2

* Fri Oct 23 2026 Dexxiez <toby@boulton.net.au> - 0.10.0-1
- Update to 0.10.0

* Thu Oct 22 2026 Dexxiez <toby@boulton.net.au> - 0.9.0-1
- Update to 0.9.0

* Wed Oct 21 2026 Dexxiez <toby@boulton.net.au> - 0.8.0-1
- Update to 0.8.0

* Tue Oct 20 2026 Dexxiez <toby@boulton.net.au> - 0.7.0-1
- Initial package
