%global forgeurl https://github.com/ryanoasis/nerd-fonts
%global fontdir  %{_datadir}/fonts
%global fcavail  %{_datadir}/fontconfig/conf.avail
%global fcconfd  %{_sysconfdir}/fonts/conf.d

# Patched families shipped as subpackages: "<asset> <subpackage-suffix>".
# To add one, append a line here and a matching SourceN below.
%global families %{expand:
JetBrainsMono jetbrains-mono
FiraCode fira-code
Hack hack
Meslo meslo
CascadiaCode cascadia-code
}

Name:           nerd-fonts
Version:        3.5.1
Release:        1%{?dist}
Summary:        Nerd Fonts symbols-only font with fontconfig fallback

# Patcher and Symbols font are MIT; the bundled glyph sets (Font Awesome,
# Material Design, Codicons, Octicons, ...) and the patched base families
# carry their own licenses.
License:        MIT AND OFL-1.1 AND Apache-2.0 AND CC-BY-4.0 AND Bitstream-Vera
URL:            https://www.nerdfonts.com
# Release assets carry no version in their names, so each is renamed on
# download so the SRPM holds one file per release.
Source0:        %{forgeurl}/releases/download/v%{version}/NerdFontsSymbolsOnly.tar.xz#/NerdFontsSymbolsOnly-%{version}.tar.xz
Source1:        %{forgeurl}/releases/download/v%{version}/JetBrainsMono.tar.xz#/JetBrainsMono-%{version}.tar.xz
Source2:        %{forgeurl}/releases/download/v%{version}/FiraCode.tar.xz#/FiraCode-%{version}.tar.xz
Source3:        %{forgeurl}/releases/download/v%{version}/Hack.tar.xz#/Hack-%{version}.tar.xz
Source4:        %{forgeurl}/releases/download/v%{version}/Meslo.tar.xz#/Meslo-%{version}.tar.xz
Source5:        %{forgeurl}/releases/download/v%{version}/CascadiaCode.tar.xz#/CascadiaCode-%{version}.tar.xz

BuildArch:      noarch

%description
Nerd Fonts patches developer-targeted fonts with a large set of icon glyphs
(Powerline, Font Awesome, Devicons, Octicons, Material Design and more).

This package ships "Symbols Nerd Font", which holds only the glyphs, plus
upstream's fontconfig snippet that makes it the icon fallback for common
monospace families. Install it to get icons with an unpatched font; the
nerd-fonts-<family> subpackages ship fully patched families instead.

Fedora's fontconfig regenerates its cache from a file trigger on %{fontdir},
so no scriptlets are needed here.

%{lua:
for line in rpm.expand("%{families}"):gmatch("[^\n]+") do
  local asset, suffix = line:match("^(%S+)%s+(%S+)$")
  print("%package " .. suffix .. "\n")
  print("Summary: " .. asset .. " patched with Nerd Fonts glyphs\n\n")
  print("%description " .. suffix .. "\n")
  print(asset .. " patched with the Nerd Fonts glyph set, in the regular,\n")
  print("Mono (single-width icons) and Propo (proportional) variants.\n\n")
  print("%files " .. suffix .. "\n")
  print("%license " .. asset .. "/LICENSE\n")
  print("%doc " .. asset .. "/README.md\n")
  local dir = rpm.expand("%{fontdir}/nerd-fonts")
  print("%dir " .. dir .. "\n")
  print(dir .. "/" .. asset .. "/\n\n")
end
}

%prep
# Every archive is flat, so unpack each into a directory named after it.
%setup -q -c -T
mkdir NerdFontsSymbolsOnly
tar -xJf %{SOURCE0} -C NerdFontsSymbolsOnly
n=1
while read -r asset suffix; do
  [ -n "$asset" ] || continue
  mkdir "$asset"
  tar -xJf "%{_sourcedir}/${asset}-%{version}.tar.xz" -C "$asset"
  # License files are named LICENSE, LICENSE.txt, LICENSE.md or OFL.txt
  # depending on the family; normalise so %%files can name one path.
  lic=$(find "$asset" -maxdepth 1 \( -name 'LICENSE*' -o -name 'OFL*' \) | head -n1)
  [ "$lic" = "$asset/LICENSE" ] || mv "$lic" "$asset/LICENSE"
done <<'EOF'
%{families}
EOF

%build
# Nothing to build; the release assets are already compiled fonts.

%install
install -d %{buildroot}%{fontdir}/nerd-fonts/NerdFontsSymbolsOnly
install -pm0644 NerdFontsSymbolsOnly/*.ttf \
    %{buildroot}%{fontdir}/nerd-fonts/NerdFontsSymbolsOnly/

install -d %{buildroot}%{fcavail} %{buildroot}%{fcconfd}
install -pm0644 NerdFontsSymbolsOnly/10-nerd-font-symbols.conf %{buildroot}%{fcavail}/
ln -s ../../..%{fcavail}/10-nerd-font-symbols.conf %{buildroot}%{fcconfd}/10-nerd-font-symbols.conf

while read -r asset suffix; do
  [ -n "$asset" ] || continue
  install -d "%{buildroot}%{fontdir}/nerd-fonts/$asset"
  install -pm0644 "$asset"/*.ttf "%{buildroot}%{fontdir}/nerd-fonts/$asset/"
done <<'EOF'
%{families}
EOF

%files
%license NerdFontsSymbolsOnly/LICENSE
%doc NerdFontsSymbolsOnly/README.md
%dir %{fontdir}/nerd-fonts
%{fontdir}/nerd-fonts/NerdFontsSymbolsOnly/
%{fcavail}/10-nerd-font-symbols.conf
%config(noreplace) %{fcconfd}/10-nerd-font-symbols.conf

%changelog
* Fri Nov 13 2026 Dexxiez <toby@boulton.net.au> - 3.5.1-1
- Initial package
