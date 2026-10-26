Name:           craft-apps
Version:        1.0.0
Release:        2%{?dist}
Summary:        Metapackage for Artcraft
License:        MIT
BuildArch:      noarch

# Hard dependencies (always installed)
Requires:       photocraft
Requires:       pdfcraft
Requires:       wordcraft
Requires:       gridcraft
Requires:       figcraft
Requires:       vectorcraft

%description
A metapackage that aggregates dependencies to install Artcraft
apps.

%prep
# Nothing to prepare

%build
# Nothing to compile

%install
# Nothing to install to the filesystem

%files
# Intentionally empty: no files are packaged

%changelog
* Tue Oct 26 2026 Dexxiez <toby@boulton.net.au> - 1.0.0-2
- Switched deps categories

* Tue Oct 20 2026 Dexxiez <toby@boulton.net.au> - 1.0.0-1
- Initial metapackage release
