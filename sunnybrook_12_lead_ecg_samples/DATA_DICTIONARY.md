# 📖 Sunnybrook Data Dictionary: Hyper-Features

This dictionary defines the **179 columns** present in `sunnybrook_master_hyperfeatures.csv`. All measurements are machine-extracted from the Philips XLI Analysis Program (Interpretation Version 10).

## 🌍 Section 1: Global Clinical Metadata
| Column | Unit | Description |
|--------|------|-------------|
| `file` | - | XML filename |
| `age` | years | Patient age as recorded by machine |
| `heart_rate` | bpm | Mean ventricular heart rate |
| `pr_interval` | ms | Global PR interval duration |
| `qrs_duration` | ms | Global QRS complex duration |
| `qt_interval` | ms | Global QT interval duration |
| `qtc` | ms | Corrected QT interval (Bazett's formula) |
| `qrs_axis` | deg | Frontal QRS axis (-180 to +180) |
| `t_axis` | deg | Frontal T-wave axis |
| `p_axis` | deg | Frontal P-wave axis |
| `diag_codes` | - | Multi-hot diagnostic strings (e.g., AFIB0, SR) |

## 📉 Section 2: Lead-Specific Morphometrics
*Note: These columns are repeated for all 12 leads: `I, II, III, aVR, aVL, aVF, V1, V2, V3, V4, V5, V6`.*

### Wave Amplitudes (Microvolts, µV)
| Variable Pattern | Description |
|------------------|-------------|
| `{LEAD}_p_amp` | P-wave peak amplitude |
| `{LEAD}_q_amp` | Q-wave peak amplitude |
| `{LEAD}_r_amp` | R-wave peak amplitude |
| `{LEAD}_s_amp` | S-wave peak amplitude |
| `{LEAD}_t_amp` | T-wave peak amplitude |

### Durations & Intervals (Milliseconds, ms)
| Variable Pattern | Description |
|------------------|-------------|
| `{LEAD}_p_dur` | P-wave duration in this lead |
| `{LEAD}_qrs_dur` | QRS duration in this lead |
| `{LEAD}_t_dur` | T-wave duration in this lead |

### ST-Segment Analysis (µV relative to isoelectric baseline)
| Variable Pattern | Description |
|------------------|-------------|
| `{LEAD}_st_on` | ST-segment onset (J-point) amplitude |
| `{LEAD}_st_mid` | ST amplitude at midpoint of segment |
| `{LEAD}_st_80` | ST amplitude at J+80ms (Primary Ischemia Metric) |
| `{LEAD}_st_end` | ST-segment termination amplitude |
| `{LEAD}_st_slope` | ST-segment slope (numeric encoded) |

### Signal Integrity
| Variable Pattern | Description |
|------------------|-------------|
| `{LEAD}_measured` | `True` if lead was physically measured (10-wire acquisition) |

## 🏷 Section 3: Primary Diagnostic Codes (Examples)
| Code | Meaning |
|------|---------|
| `SR` | Sinus Rhythm |
| `SB` | Sinus Bradycardia |
| `ST` | Sinus Tachycardia |
| `AFIB0` | Atrial Fibrillation |
| `AFLT` | Atrial Flutter |
| `IMIC` | Inferior MI, confirmed |
| `MSTEA` | Minimal ST elevation, anterior |
| `LVOLF` | Low voltage, frontal leads |
| `MISLDS`| Mislaced leads (Warning) |
