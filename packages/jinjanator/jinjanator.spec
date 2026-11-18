Name:           jinjanator
Version:        26.3.0
Release:        1%{?dist}
Summary:        Command-line interface to Jinja2 for templating in shell scripts

License:        Apache-2.0
URL:            https://github.com/kpfleming/jinjanator
Source0:        %{pypi_source jinjanator}

BuildArch:      noarch

BuildRequires:  python3-devel

# Not in Fedora; built from packages/python-jinjanator-plugins in this repo.
Requires:       python3-jinjanator-plugins

%description
jinjanator (j2) renders Jinja2 templates from the command line, with data
taken from environment variables, INI, JSON, YAML or .env files. Supports
plugins via jinjanator-plugins.

%prep
%autosetup -n %{name}-%{version}

%generate_buildrequires
# -R: skip runtime deps so the build doesn't need jinjanator-plugins
# (only in this COPR) to exist in the buildroot first.
%pyproject_buildrequires -R

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l jinjanator

# No %%check: importing jinjanator needs jinjanator-plugins, which is
# deliberately not a BuildRequires (see above).

%files -f %{pyproject_files}
%doc README.md CHANGELOG.md
%{_bindir}/j2
%{_bindir}/jinjanate

%changelog
* Wed Nov 18 2026 Dexxiez <toby@boulton.net.au> - 26.3.0-1
- Initial package
