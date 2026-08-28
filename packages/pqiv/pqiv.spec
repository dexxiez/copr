%global forgeurl https://github.com/phillipberndt/pqiv

Name:           pqiv
Version:        2.13.3
Release:        1%{?dist}
Summary:        Powerful command-line GTK image viewer

License:        GPL-3.0-or-later
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  pkgconf-pkg-config
BuildRequires:  desktop-file-utils
BuildRequires:  gtk3-devel
BuildRequires:  poppler-glib-devel
BuildRequires:  libspectre-devel
BuildRequires:  libwebp-devel
BuildRequires:  libarchive-devel
BuildRequires:  ImageMagick-devel

%description
pqiv is a GTK-based command-line image viewer with a minimal UI, aimed at
being scriptable and usable as a lightweight replacement for a full desktop
image viewer. It supports thumbnails, slideshows, basic editing actions and,
via optional backends, PDF, PostScript, WebP, archives/comic books and
additional formats through ImageMagick.

This build links all detected backends statically into the pqiv binary,
which is pqiv's own default (%{name}'s configure script defaults to
--backends-build=static).

%prep
%autosetup -n %{name}-%{version}

%build
%set_build_flags
./configure --prefix=%{_prefix} --libdir=%{_libdir}
%make_build

%install
%make_install PREFIX=%{_prefix} MANDIR=%{_mandir}

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%license LICENSE
%doc README.markdown
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{_datadir}/applications/%{name}.desktop

%changelog
* Fri Aug 28 2026 Dexxiez <toby@boulton.net.au> - 2.13.3-1
- Initial package
