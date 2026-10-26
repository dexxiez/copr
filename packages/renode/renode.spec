%global forgeurl https://github.com/renode/renode
%global instdir  %{_libdir}/%{name}

# Built by upstream's build.sh rather than Fedora's macros, and the payload
# is mostly managed .NET assemblies. Skip the debuginfo subpackage.
%global debug_package %{nil}

# bin/Lib is IronPython's bundled (Python 2) stdlib. Its modules are imported
# by Renode, never executed, so leave their shebangs alone and don't turn them
# into requirements (cgi.py alone would pull in /usr/local/bin/python).
%global __brp_mangle_shebangs_exclude_from ^%{instdir}/
%global __requires_exclude_from ^%{instdir}/bin/Lib/.*$
%global __provides_exclude_from ^%{instdir}/.*$

Name:           renode
Version:        1.17.0
Release:        1%{?dist}
Summary:        Virtual development framework for complex embedded systems

License:        MIT
URL:            https://renode.io
# Upstream's source release asset bundles all git submodules, the NuGet
# packages and renode-resources.
Source0:        %{forgeurl}/releases/download/v%{version}/%{name}_%{version}_source.tar.xz

BuildRequires:  dotnet-sdk-8.0
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  make
BuildRequires:  desktop-file-utils

Requires:       dotnet-runtime-8.0
Requires:       gtk3
Requires:       webkit2gtk4.1
# Mirrors the dependencies of upstream's own fpm-built RPM.
Recommends:     gcc
Recommends:     libgdiplus
Recommends:     screen
Recommends:     polkit

# tlib's code generator only has i386 (x86_64) and aarch64 host backends.
ExclusiveArch:  x86_64 aarch64

%description
Renode is a development framework which accelerates IoT and embedded systems
development by letting you simulate physical hardware systems, including the
CPU, peripherals, sensors, environment and wired or wireless communication
between nodes. It runs unmodified firmware binaries for Arm, RISC-V, x86,
PowerPC, SPARC and Xtensa targets.

This package does not include renode-test (the Robot Framework test runner).

%prep
%autosetup -n %{name}_%{version}_source
# The bundled NuGet cache was restored with whatever SDK upstream used, so
# its targeting/ref packs won't match Fedora's dotnet-sdk-8.0 patch level.
# Keep the local cache first and fall back to nuget.org for the rest, which
# COPR's buildroots permit.
sed -i 's|<add key="local-packages" value="./nuget" />|&\n    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />|' NuGet.Config
grep -q api.nuget.org NuGet.Config

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_NOLOGO=1
export NUGET_PACKAGES="%{_builddir}/.nuget"
# Several bundled libraries are strong-name signed, which Roslyn does with
# RSA/SHA-1. Fedora's crypto policy rejects SHA-1 signatures in OpenSSL
# ("invalid digest") unless this override is set.
export OPENSSL_ENABLE_SHA1_SIGNATURES=1
# Without a .git directory build.sh skips submodule/resource fetching.
./build.sh

%install
out=output/bin/Release
dest=%{buildroot}%{instdir}

# Same selection as upstream's tools/packaging/common_copy_files_package.sh
install -d $dest/bin
cp -P $out/*.dll $dest/bin/
rm -f $dest/bin/*Tests.dll $dest/bin/RenodeWPF.dll
cp -P $out/*.dll.config $dest/bin/ 2>/dev/null || :
cp -pr $out/platform-lib $out/runtimes $out/Lib $dest/bin/
cp -p $out/Renode.runtimeconfig.json $out/Renode.deps.json $dest/bin/
rm -rf $dest/bin/Lib/{ensurepip,distutils,lib2to3,pydoc_data}

# Drop Windows-only NuGet assets, keeping runtimes/unix (as upstream's
# own Linux package does).
rm -rf $dest/bin/runtimes/win*

# Renode locates its scripts/platforms by walking up to .renode-root.
cp -pr .renode-root scripts platforms $dest/

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/renode <<'SH'
#!/usr/bin/sh
exec dotnet %{instdir}/bin/Renode.dll "$@"
SH
chmod 0755 %{buildroot}%{_bindir}/renode

install -Dpm0644 tools/packaging/linux/Renode.desktop \
    %{buildroot}%{_datadir}/applications/Renode.desktop
install -d %{buildroot}%{_datadir}/icons
cp -pr tools/packaging/linux/icons %{buildroot}%{_datadir}/icons/hicolor

# Collect the licenses of tlib, bundled libraries and resources.
mkdir licenses
tools/packaging/common_copy_licenses.sh licenses linux

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/Renode.desktop
dotnet %{buildroot}%{instdir}/bin/Renode.dll --version

%files
%license licenses/*
%doc README.md CHANGELOG.rst
%{_bindir}/renode
%{instdir}
%{_datadir}/applications/Renode.desktop
%{_datadir}/icons/hicolor/*/apps/renode.*

%changelog
* Mon Oct 26 2026 Dexxiez <toby@boulton.net.au> - 1.17.0-1
- Initial package
