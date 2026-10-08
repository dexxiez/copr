%global modelurl https://ocrs-models.s3-accelerate.amazonaws.com

Name:           pdfcraft-ocr-models
# The models carry no version; the snapshot date is their upload date.
Version:        0^20240101
Release:        1%{?dist}
Summary:        Text detection and recognition models for PdfCraft's Scan & OCR

License:        CC-BY-SA-4.0
URL:            https://github.com/robertknight/ocrs-models
Source0:        %{modelurl}/text-detection.rten
Source1:        %{modelurl}/text-recognition.rten
Source2:        https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt#/LICENSE-CC-BY-SA-4.0.txt

BuildArch:      noarch
Requires:       pdfcraft

%description
The pre-trained ocrs models (by Robert Knight, trained on HierText) that
PdfCraft uses for Scan & OCR: one finds words on page images, the other
reads them. They read the Latin alphabet without accents.

Installed to %{_datadir}/pdfcraft/models, where pdfcraft looks for them.

%prep
# Same SHA-256s pdfcraft pins in its ATTRIBUTION.toml.
echo "f15cfb56bd02c4bf478a20343986504a1f01e1665c2b3a0ad66340f054b1b5ca  %{SOURCE0}" | sha256sum -c
echo "e484866d4cce403175bd8d00b128feb08ab42e208de30e42cd9889d8f1735a6e  %{SOURCE1}" | sha256sum -c
echo "28a9529c7d0bb4dc51f4bf5c116a3d16ef247a052f7591466768ddf563fd1cf5  %{SOURCE2}" | sha256sum -c
cp -p %{SOURCE2} .

%install
install -Dpm0644 %{SOURCE0} %{buildroot}%{_datadir}/pdfcraft/models/text-detection.rten
install -Dpm0644 %{SOURCE1} %{buildroot}%{_datadir}/pdfcraft/models/text-recognition.rten

%files
%license LICENSE-CC-BY-SA-4.0.txt
%dir %{_datadir}/pdfcraft
%{_datadir}/pdfcraft/models/

%changelog
* Thu Oct 08 2026 Dexxiez <toby@boulton.net.au> - 0^20240101-1
- Initial package
