# 🏥 Sunnybrook Clinical Validation Set (Philips Sierra XML)

## 📋 Dataset Overview
This dataset contains **20 high-fidelity 12-lead ECG records** provided by the Sunnybrook Health Sciences Centre for the external validation of the Fa-MAE foundation model and the mEcgNet reconstruction bridge.

Unlike public datasets where Lead-III or Augmented leads are often mathematically derived, these records are **fully measured (10-wire acquisition)**, providing a gold-standard reference for spatial imputation.

## 🛠 Technical Specifications
| Parameter | Value |
|-----------|-------|
| **Source** | Sunnybrook Health Sciences Centre |
| **Hardware** | Philips PageWriter TC (TC70/TC50 series) |
| **Format** | Philips Sierra XML (XLI Compressed) |
| **Sampling Rate** | 500 Hz |
| **Resolution** | 5 µV per Bit (16-bit signed) |
| **Filters** | High-pass: 0.05 Hz \| Low-pass: 150 Hz \| Notch: 60 Hz |
| **Lead Set** | Standard 12-Lead (I, II, III, aVR, aVL, aVF, V1-V6) |

## 🧬 Clinical Composition
The set is curated to include both normal and pathological cardiac states:
- **Baseline**: Sinus Rhythm, Sinus Bradycardia.
- **Pathology**: Atrial Fibrillation (AFib), Atrial Flutter (AFL), Old Inferior MI.
- **Morphology**: Left Atrial Enlargement, Incomplete RBBB, Poor R-wave progression.
- **Artifacts**: One record (`MISLDS`) specifically flags "Mislaced Leads" for prior-sensitivity testing.

## 📏 Known Limitations (Auditor's Note)
- **Physical Einthoven Residual**: There is a measured residue of ~18µV in the `II - I = III` relationship. This is attributed to physical hardware noise and skin-electrode impedance. Any model error below this threshold is considered "noise reconstruction."
- **Representative Beats (RepBeats)**: The dataset includes 1200-sample (2.4s) averaged representative beats for detailed morphometric analysis.

## 📂 File Structure
- `*.xml`: Raw Philips Sierra XML files.
- `sunnybrook_master_hyperfeatures.csv`: 179-column clinical morphometric reference.
- `DATA_DICTIONARY.md`: Definition of all extracted features.
