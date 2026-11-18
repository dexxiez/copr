%global pypi_name jinjanator-plugins

Name:           python-%{pypi_name}
Version:        26.2.0
Release:        1%{?dist}
Summary:        Plugin API for the jinjanator tool

License:        Apache-2.0
URL:            https://github.com/kpfleming/jinjanator-plugins
Source0:        %{pypi_source jinjanator_plugins}

BuildArch:      noarch

BuildRequires:  python3-devel

%global _description %{expand:
Package which provides the plugin API for jinjanator, a command-line
interface to Jinja2 for templating in shell scripts.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n jinjanator_plugins-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l jinjanator_plugins

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.md CHANGELOG.md

%changelog
* Wed Nov 18 2026 Dexxiez <toby@boulton.net.au> - 26.2.0-1
- Initial package
