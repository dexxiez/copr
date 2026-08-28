%global forgeurl https://github.com/mwh/dragon
%global upname   dragon

# Fedora already ships a package called "dragon" (KDE's Dragon Player), so the
# binary and man page are built under the name other distros use for this tool.
# The Makefile's NAME variable renames both.

Name:           dragon-drop
Version:        1.2.0
Release:        1%{?dist}
Summary:        Lightweight drag-and-drop source and sink for X or Wayland

License:        GPL-3.0-or-later
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/v%{version}/%{upname}-%{version}.tar.gz
# Completions were added upstream in 2b90e5f (2025-08-03), well after the last
# tag, so they are vendored here rather than taken from the tarball. Every
# option the script offers exists in 1.2.0. Drop this once upstream tags a
# release that ships it.
Source1:        %{name}.bash-completion

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  pkgconfig(gtk+-3.0)

%description
dragon opens a small window holding the files given on its command line, ready
to be dragged into any application that accepts drops. With --target it works
the other way round, printing the paths of whatever is dropped onto it, which
makes it a way to drive drag-and-drop from a shell or a file-less window
manager setup.

%prep
%autosetup -n %{upname}-%{version}

%build
# The Makefile hardcodes its compile line and ignores CFLAGS/LDFLAGS, but it
# does interpolate DEFINES ahead of the source file, which is enough to get
# Fedora's build and hardening flags in.
%make_build NAME=%{name} DEFINES="%{build_cflags} %{build_ldflags}"

%install
%make_install NAME=%{name} PREFIX=%{_prefix} MANPREFIX=%{_datadir}/man

# The completion registers itself against the upstream command name; point it
# at the renamed binary instead.
install -d %{buildroot}%{_datadir}/bash-completion/completions
sed -e 's/ %{upname}$/ %{name}/' %{SOURCE1} \
    > %{buildroot}%{_datadir}/bash-completion/completions/%{name}

%files
%license LICENCE
%doc README
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{_datadir}/bash-completion/completions/%{name}

%changelog
* Fri Aug 28 2026 Dexxiez <toby@boulton.net.au> - 1.2.0-1
- Initial package
