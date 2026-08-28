%global forgeurl https://github.com/subframe7536/maple-font
%global fontname maple-mono
%global fontdir  %{_datadir}/fonts

Name:           maple-fonts
Version:        7.9
Release:        1%{?dist}
Summary:        Open source monospace font with round corners and ligatures

License:        OFL-1.1
URL:            %{forgeurl}
# Upstream ships prebuilt release assets rather than a source tarball; the
# asset names carry no version, so each is renamed on download so the SRPM
# holds one file per release.
Source0:        %{forgeurl}/releases/download/v%{version}/MapleMono-TTF.zip#/MapleMono-TTF-%{version}.zip
Source1:        %{forgeurl}/releases/download/v%{version}/MapleMono-NF.zip#/MapleMono-NF-%{version}.zip

BuildArch:      noarch
BuildRequires:  unzip

%description
Maple Mono is a monospace font with rounded corners, programming ligatures
and a hand-tuned italic. This package ships the TTF build of the base family
in sixteen upright and italic weights.

Fedora's fontconfig regenerates its cache from a file trigger on %{fontdir},
so no scriptlets are needed here.

%package nf
Summary:        Maple Mono patched with Nerd Fonts glyphs
Requires:       %{name} = %{version}-%{release}

%description nf
Maple Mono NF is the same family patched with the Nerd Fonts glyph set
(Powerline, Font Awesome, Devicons and friends), for terminals and editors
that draw icons from the private use area.

%prep
# Both archives are flat, so unpack each into its own directory.
%setup -q -c -T
mkdir -p ttf nf
unzip -q -d ttf %{SOURCE0}
unzip -q -d nf  %{SOURCE1}

%build
# Nothing to build; the release assets are already compiled fonts.

%install
install -d %{buildroot}%{fontdir}/%{fontname}
install -pm0644 ttf/MapleMono-*.ttf %{buildroot}%{fontdir}/%{fontname}/

install -d %{buildroot}%{fontdir}/%{fontname}-nf
install -pm0644 nf/MapleMono-NF-*.ttf %{buildroot}%{fontdir}/%{fontname}-nf/

%files
%license ttf/LICENSE.txt
%dir %{fontdir}/%{fontname}
%{fontdir}/%{fontname}/MapleMono-*.ttf

%files nf
%license nf/LICENSE.txt
%dir %{fontdir}/%{fontname}-nf
%{fontdir}/%{fontname}-nf/MapleMono-NF-*.ttf

%changelog
* Fri Aug 28 2026 Dexxiez <toby@boulton.net.au> - 7.9-1
- Initial package
