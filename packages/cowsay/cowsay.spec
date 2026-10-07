%global forgeurl https://github.com/cowsay-org/cowsay

# Snapshot of the main branch. check_updates.py rewrites `commit` and the
# snapshot suffix of Version together; the base (before `^`) is bumped by hand.
%global commit af5d2334ce8c594071041e15cba77e674023c082
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           cowsay
Version:        3.8.4^20251224gitaf5d233
Release:        1%{?dist}
Summary:        Configurable speaking/thinking cow

License:        GPL-3.0-or-later
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/%{commit}.tar.gz#/%{name}-%{shortcommit}.tar.gz
# Restores cows dropped upstream (satanic, sodomized, telebears).
Patch0:         original_cows.patch

BuildArch:      noarch

BuildRequires:  make
BuildRequires:  perl-generators
BuildRequires:  perl-interpreter
# For %%check
BuildRequires:  perl(Cwd)
BuildRequires:  perl(File::Basename)
BuildRequires:  perl(File::Find)
BuildRequires:  perl(Getopt::Std)
BuildRequires:  perl(Text::Tabs)
BuildRequires:  perl(Text::Wrap)

%description
cowsay generates an ASCII picture of a cow saying something provided by the
user. cowthink does the same, but the cow is thinking instead. Many other
"cows" are included and can be selected with -f.

This build tracks the upstream main branch and restores the original cows
that were removed upstream.

%prep
%autosetup -n %{name}-%{commit} -p1

%build
# Nothing to build; the Makefile's default target is a no-op.

%install
%make_install prefix=%{_prefix} sysconfdir=%{_sysconfdir}

%check
./bin/cowsay moo
./bin/cowthink -f satanic moo

%files
%license LICENSE*.txt
%doc README.md CHANGELOG.md
%{_bindir}/cowsay
%{_bindir}/cowthink
%{_mandir}/man1/cowsay.1*
%{_mandir}/man1/cowthink.1*
%{_datadir}/%{name}/
%{_sysconfdir}/%{name}/

%changelog
* Wed Oct 07 2026 Dexxiez <toby@boulton.net.au> - 3.8.4^20251224gitaf5d233-1
- Initial package, snapshot of main with original cows restored
