%global forgeurl https://github.com/WestberryTech/wb32-dfu-updater

Name:           wb32-dfu-updater
Version:        1.0.0
Release:        1%{?dist}
Summary:        Flash firmware to and from WB32 MCUs over USB DFU

License:        Apache-2.0
URL:            %{forgeurl}
# Upstream's newest tag is unprefixed; older ones (v0.0.x) carry a "v".
Source0:        %{forgeurl}/archive/%{version}/%{name}-%{version}.tar.gz
# Upstream ships no udev rule, so flashing would need root. This grants the
# logged-in user access to the WB32 bootloader (342d:dfa0), matching the
# entry in QMK's udev rules.
Source1:        70-wb32-dfu.rules

BuildRequires:  gcc
# project() names no LANGUAGES, so CMake probes for a C++ compiler too.
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  pkgconfig(libusb-1.0)
BuildRequires:  systemd-rpm-macros

%description
wb32-dfu-updater_cli is Westberry Technology's host tool for downloading and
uploading firmware to and from WB32 microcontrollers via their USB bootloader.
It is the flasher QMK uses for WB32-based keyboards.

%prep
%autosetup

%build
# CMakeLists.txt declares cmake_minimum_required(3.0), which CMake 4 rejects;
# upstream fixed this after 1.0.0. Without an explicit Release build type it
# forces Debug.
%cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5
%cmake_build

%install
%cmake_install
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/70-wb32-dfu.rules

%files
%license LICENSE
%doc README.md
%{_bindir}/wb32-dfu-updater_cli
%{_udevrulesdir}/70-wb32-dfu.rules

%changelog
* Mon Oct 26 2026 Dexxiez <toby@boulton.net.au> - 1.0.0-1
- Initial package
