%global forgeurl https://github.com/neovim/neovim

# The bundled dependencies (luajit, tree-sitter, libvterm, ...) are built as
# static libraries with their own flags, so the debuginfo extractor finds
# nothing consistent to package. Skip the subpackage rather than fight it.
%global debug_package %{nil}

Name:           neovim
Version:        0.12.5
Release:        1%{?dist}
Summary:        Vim-fork focused on extensibility and usability

License:        Apache-2.0 AND Vim
URL:            https://neovim.io
Source0:        %{forgeurl}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake >= 3.16
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
# The po/ targets need msgfmt, msgmerge and xgettext all present, or the
# translations are silently skipped and %%find_lang finds nothing.
BuildRequires:  gettext
# cmake.deps downloads each dependency's release tarball and verifies it
BuildRequires:  curl
BuildRequires:  git-core
BuildRequires:  unzip
BuildRequires:  patch
# desktop file and icon are validated/installed by the build
BuildRequires:  desktop-file-utils

# Neovim is usable without these, but a bare install is a poor experience:
# most plugin managers shell out to git, and :checkhealth warns without a
# clipboard provider or a modern grep.
Recommends:     git-core
Recommends:     xclip
Recommends:     ripgrep
Recommends:     fd-find

Provides:       nvim = %{version}-%{release}

ExclusiveArch:  x86_64 aarch64

%description
Neovim is a refactor of Vim that keeps the same editing model and configuration
language while modernising the parts underneath: a real API over msgpack-rpc,
built-in LSP and tree-sitter support, an embedded Lua runtime, asynchronous
jobs, and a proper built-in terminal emulator.

This package builds against Neovim's own bundled dependencies rather than the
distribution's, so the editor tracks upstream releases without waiting on
libvterm, tree-sitter or luajit to catch up.

%prep
%autosetup -n %{name}-%{version}

%build
# Dependencies first. These are vendored source tarballs fetched at configure
# time and built static into .deps; they are deliberately NOT given Fedora's
# build flags, since several of them fail the hardening checks.
cmake -S cmake.deps -B .deps -G Ninja \
      -D CMAKE_BUILD_TYPE=RelWithDebInfo \
      -D USE_BUNDLED=ON
cmake --build .deps

cmake -B build -G Ninja \
      -D CMAKE_BUILD_TYPE=RelWithDebInfo \
      -D CMAKE_INSTALL_PREFIX=%{_prefix} \
      -D CMAKE_INSTALL_LIBDIR=%{_lib} \
      -D CMAKE_INSTALL_MANDIR=%{_mandir} \
      -D CMAKE_PREFIX_PATH=$PWD/.deps/usr \
      -D ENABLE_LTO=ON \
      -D ENABLE_TRANSLATIONS=ON
cmake --build build

%install
DESTDIR=%{buildroot} cmake --install build

desktop-file-validate %{buildroot}%{_datadir}/applications/nvim.desktop

%find_lang nvim

%check
# Runs against the buildroot copy so the runtime files it needs are in place.
VIMRUNTIME=%{buildroot}%{_datadir}/nvim/runtime \
    %{buildroot}%{_bindir}/nvim --version
VIMRUNTIME=%{buildroot}%{_datadir}/nvim/runtime \
    %{buildroot}%{_bindir}/nvim --headless +q

%files -f nvim.lang
%license LICENSE.txt
%doc README.md
%{_bindir}/nvim
%{_datadir}/nvim/
%{_datadir}/applications/nvim.desktop
%{_datadir}/icons/hicolor/*/apps/nvim.png
%{_mandir}/man1/nvim.1*
%{_libdir}/nvim/

%changelog
* Fri Aug 28 2026 Dexxiez <toby@boulton.net.au> - 0.12.5-1
- Initial package
