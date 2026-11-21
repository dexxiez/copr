Name:           pdfcraft-ocr-models
# The models carry no version; the snapshot date is their upload date (S3 Last-Modified).
Version:        0^20260913
Release:        1%{?dist}
Summary:        Text detection and recognition models for PdfCraft's Scan & OCR

License:        CC-BY-SA-4.0
URL:            https://github.com/robertknight/ocrs-models
# Vendored in this repo (upstream S3 has removed files before). Fetched from
# https://ocrs-models.s3-accelerate.amazonaws.com/<name>.onnx and
# https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt
Source0:        text-detection.onnx
Source1:        text-recognition.onnx
Source2:        LICENSE-CC-BY-SA-4.0.txt

BuildArch:      noarch
Requires:       pdfcraft

%description
The pre-trained ocrs models (by Robert Knight, trained on HierText) that
PdfCraft uses for Scan & OCR: one finds words on page images, the other
reads them. They read the Latin alphabet without accents.

Installed to %{_datadir}/pdfcraft/models, where pdfcraft looks for them.

%prep
# Same SHA-256s pdfcraft pins in its ATTRIBUTION.toml.
echo "a917b23dbd9524b465df7e922641b3ff2981623df4ded5a0234004ef2fee7cfe  %{SOURCE0}" | sha256sum -c
echo "86c145c2edb96c8caed5b1ebb8f44d706408922211451c309c625157dd6061c5  %{SOURCE1}" | sha256sum -c
echo "28a9529c7d0bb4dc51f4bf5c116a3d16ef247a052f7591466768ddf563fd1cf5  %{SOURCE2}" | sha256sum -c
cp -p %{SOURCE2} .

%install
install -Dpm0644 %{SOURCE0} %{buildroot}%{_datadir}/pdfcraft/models/text-detection.onnx
install -Dpm0644 %{SOURCE1} %{buildroot}%{_datadir}/pdfcraft/models/text-recognition.onnx

%files
%license LICENSE-CC-BY-SA-4.0.txt
%dir %{_datadir}/pdfcraft
%{_datadir}/pdfcraft/models/

%changelog
* Sat Nov 21 2026 Dexxiez <toby@boulton.net.au> - 0^20260913-1
- Switch to upstream ONNX models; the .rten files were removed from S3
- Vendor the models and licence text in the repo

* Thu Oct 08 2026 Dexxiez <toby@boulton.net.au> - 0^20240101-1
- Initial package
