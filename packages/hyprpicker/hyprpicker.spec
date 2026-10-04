%global forgeurl https://github.com/hyprwm/hyprpicker

Name:           hyprpicker
Version:        0.4.7
Release:        1%{?dist}
Summary:        A wlroots-compatible Wayland color picker

License:        BSD-3-Clause
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig
# hyprwayland-scanner-devel ships the /usr/bin/hyprwayland-scanner generator
# that CMakeLists invokes for every protocol, as well as its .pc file.
BuildRequires:  pkgconfig(hyprwayland-scanner) >= 0.4.0
BuildRequires:  pkgconfig(hyprutils) >= 0.2.0
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-protocols)
# pkg_get_variable(... wayland-scanner pkgdatadir) needs this for wayland.xml.
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(libjpeg)

%description
hyprpicker grabs a screen copy of every output and lets you pick a colour from
anywhere on screen, printing it to stdout as hex, RGB, HSV, HSL or CMYK. It
talks plain wlr-screencopy and wlr-layer-shell, so it works on any
wlroots-compatible compositor and needs nothing from Hyprland itself.

%prep
%autosetup

%build
%cmake
%cmake_build

%install
%cmake_install

%check
# No display in the build root, so only the argument parser can be exercised.
%{__cmake_builddir}/%{name} --version

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*

%changelog
* Mon Oct 05 2026 Dexxiez <toby@boulton.net.au> - 0.4.7-1
- Initial package
