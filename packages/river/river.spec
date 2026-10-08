%global forgeurl https://codeberg.org/river/river

# Built with -Dstrip, so an empty debuginfo subpackage would fail.
%global debug_package %{nil}

Name:           river
Version:        0.4.8
Release:        2%{?dist}
Summary:        Non-monolithic Wayland compositor

# Compositor is GPL-3.0-only; protocol XML (protocols-devel) is MIT.
License:        GPL-3.0-only AND MIT
URL:            %{forgeurl}
# Signed release tarballs, as recommended by upstream's PACKAGING.md. Key from
# https://isaacfreund.com/public_key.txt (Isaac Freund, river maintainer).
Source0:        %{forgeurl}/releases/download/v%{version}/%{name}-%{version}.tar.gz
Source1:        %{forgeurl}/releases/download/v%{version}/%{name}-%{version}.tar.gz.sig
Source2:        gpgkey-5FBDF84DD2278DB2B8AD8A5286DED400DDFD7A11.asc

# River only builds with the latest Zig minor release (0.16 at time of writing).
BuildRequires:  zig >= 0.16
BuildRequires:  zig < 0.17
BuildRequires:  scdoc
BuildRequires:  gnupg2
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wlroots-0.20)
BuildRequires:  pkgconfig(xkbcommon) >= 1.12
BuildRequires:  pkgconfig(libevdev)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(pixman-1)

Recommends:     xorg-x11-server-Xwayland

ExclusiveArch:  %{zig_arches}

%description
River is a non-monolithic Wayland compositor. Unlike other Wayland
compositors, river does not combine the compositor and window manager into
one program. Instead, users can choose any window manager implementing the
river-window-management-v1 protocol.

%package        protocols-devel
Summary:        River Wayland protocol XML files
License:        MIT
BuildArch:      noarch
Requires:       pkgconfig
Requires:       pkgconfig(wayland-server)
Requires:       pkgconfig(wayland-protocols)
Requires:       pkgconfig(wlroots-0.20)
Requires:       pkgconfig(xkbcommon) >= 1.12
Requires:       pkgconfig(libevdev)
Requires:       pkgconfig(libinput)
Requires:       pkgconfig(pixman-1)

%description    protocols-devel
Protocol XML files and pkg-config metadata for writing river window managers
and clients.

%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%autosetup

%build
# Zig package dependencies (build.zig.zon) are fetched from codeberg here, so
# the COPR project needs networking enabled for builds.
export ZIG_GLOBAL_CACHE_DIR="%{_builddir}/.cache/zig"
DESTDIR="%{_builddir}/destdir" zig build install \
    -j%{_smp_build_ncpus} \
    --prefix %{_prefix} \
    -Doptimize=ReleaseSafe \
    -Dcpu=baseline \
    -Dpie \
    -Dstrip \
    -Dxwayland \
    -Dman-pages \
    -Dversion-string=%{version}

%install
mkdir -p %{buildroot}
cp -a %{_builddir}/destdir/. %{buildroot}/

%check
%{buildroot}%{_bindir}/%{name} -version

%files
%license LICENSES/GPL-3.0-only.txt
%doc README.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*

%files protocols-devel
%license LICENSES/MIT.txt
%{_datadir}/pkgconfig/river-protocols.pc
%{_datadir}/river-protocols/

%changelog
* Thu Oct 08 2026 Dexxiez <toby@boulton.net.au> - 0.4.8-2
- protocols-devel: require the devel packages river builds against

* Tue Oct 06 2026 Dexxiez <toby@boulton.net.au> - 0.4.8-1
- Initial package
