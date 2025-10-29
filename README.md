# 🏥 Fitbit Clinical Dashboard — Pilot Feasibility Study

**Multi-Participant AFib Monitoring System for Clinical Studies (pilot feasibility)**

A comprehensive dashboard for managing and analyzing Fitbit ECG data from multiple participants in clinical atrial fibrillation (AFib) monitoring studies.

---

## 📋 Overview

This dashboard was developed for the **Sunnybrook Health Sciences Centre AFib Monitoring Pilot Feasibility Study**, enabling researchers to:

- Monitor **20 participants** (10 ablation + 10 cardioversion arms)
- Track **daily ECG compliance** and adherence metrics
- View and analyze **ECG waveforms** with R-peak detection
- Manage **participant enrollment** and device assignment
- Export data in **batch mode** for all participants
- Maintain **HIPAA-compliant local storage**

---

## 🎯 Study Design (Pilot Feasibility)

| Arm | Participants | Monitoring Period | Target Adherence |
|-----|--------------|-------------------|------------------|
| **Ablation** | 10 | 6 months (post-blanking) | 70% daily ECGs |
| **Cardioversion** | 10 | 3-6 months | 70% daily ECGs |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Fitbit Developer Account
- Study-created email accounts for each participant

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/fitbit-clinical-dashboard.git
cd fitbit-clinical-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Set up Fitbit API credentials** in `fitbit/config.py`:
```python
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
REDIRECT_URI = 'http://localhost:8080/'
```

2. **Initialize participant registry**:
```bash
# Edit fitbit/participants.csv with your study participants
```

### Running the Dashboard

```bash
# Start the dashboard
streamlit run dashboard/app.py --server.port 8502

# Open browser to http://localhost:8502
```

---

## 📊 Dashboard Usage

### Quick Actions Bar

| Action | Description | Command |
|--------|-------------|---------|
| 🔄 **Refresh Data** | Reload all participant data | Click button |
| 📥 **Batch Export** | Export all participants | `python scripts/batch_export_all.py` |
| 👥 **View Compliance** | See adherence metrics | Switch to Compliance tab |
| 🔐 **Authorize** | Setup new participant | `python fitbit/get_fitbit_token.py --participant <ID>` |

### Study Overview Metrics

- **Total Participants**: Current enrollment count
- **Ablation Arm**: Progress towards 10 participants
- **Cardioversion Arm**: Progress towards 10 participants
- **Active (48h)**: Participants with recent ECG data
- **Overall Adherence**: Percentage meeting 70% target

### Tabs

1. **Waveforms**: View and analyze individual ECG recordings
2. **Compliance**: Monitor adherence across all participants
3. **Participants**: Manage enrollment and device assignment

---

## 🔐 Authentication Workflow

### For Each New Participant:

1. **Create study email account** (e.g., `study-abl01@sunnybrook.ca`)
2. **Register Fitbit account** with study email
3. **Run authorization** on secure Sunnybrook machine:
```bash
python fitbit/get_fitbit_token.py --participant ABL01
```
4. **Token stored** at `fitbit/tokens/ABL01.json`
5. **Data exported** to `fitbit_exports/ABL01/`

### Security Notes:
- ⚠️ **Run authentication ONLY on password-protected Sunnybrook machines**
- ⚠️ **Do NOT use personal Fitbit accounts**
- ⚠️ **Do NOT upload tokens to cloud storage**
- ✅ **All data stored locally on Sunnybrook machines**

---

## 📥 Data Export

### Single Participant:
```bash
python fitbit/run_export_ecg.py 2025-01-01 2025-01-31 fitbit_exports/ABL01 ABL01 --cardiac-only --verbose --participant ABL01
```

### All Participants (Batch):
```bash
python scripts/batch_export_all.py --days 7 --cardiac-only --verbose
```

### Output Structure:
```
fitbit_exports/
├── ABL01/
│   ├── ECG_summary.csv
│   ├── ECG_waveforms_index.csv
│   ├── ecg_waveforms/
│   │   └── *.csv
│   ├── daily_cardiac_summary.csv
│   └── af_scores.csv
├── ABL02/
│   └── ...
```

---

## 👥 Participant Registry

### Adding New Participants:

1. **Via Dashboard**:
   - Go to "Participants" tab
   - Fill in the form:
     - Study ID (e.g., ABL01, CVR01)
     - First/Last Name
     - Email (study account)
     - Phone
     - Start/End Dates
     - Expected ECGs/Day (default: 2)
     - Device ID
     - Status (invited/enrolled/paused/withdrawn)
   - Click "Save/Update participant"

2. **Via CSV**:
   - Edit `fitbit/participants.csv` directly
   - Columns: `studyId,firstName,lastName,phone,email,deviceId,status,startDate,endDate,expectedPerDay,notes`

---

## 📈 Compliance Monitoring

### Metrics:

- **Observed ECGs**: Total recordings to date
- **Expected ECGs**: Based on `(days_since_start × expected_per_day)`
- **Compliance %**: `(observed / expected) × 100`
- **Last ECG**: Timestamp of most recent recording
- **7-Day Rate**: Recent week completion percentage
- **Artifact Ratio**: Percentage marked as artifacts
- **Inconclusive Ratio**: Percentage with inconclusive classification

### Alert Thresholds (Configurable):

- **Stale ECG**: > 2 days since last recording
- **Low 7-Day**: < 30% completion in past week

---

## 🛠️ Troubleshooting

### Common Issues:

**1. "No tokens found" error:**
```bash
# Solution: Run authorization for that participant
python fitbit/get_fitbit_token.py --participant <STUDY_ID>
```

**2. "ECG_summary.csv not found":**
```bash
# Solution: Export data for that participant
python fitbit/run_export_ecg.py <START_DATE> <END_DATE> fitbit_exports/<STUDY_ID> <STUDY_ID> --participant <STUDY_ID>
```

**3. "Port 8502 already in use":**
```bash
# Solution: Use different port
streamlit run dashboard/app.py --server.port 8503
```

**4. Token expired:**
```bash
# Tokens auto-refresh, but if issues persist:
# Re-run authorization for that participant
python fitbit/get_fitbit_token.py --participant <STUDY_ID>
```

---

## 📁 Project Structure

```
fitbit-clinical-dashboard/
├── dashboard/
│   └── app.py                    # Main Streamlit dashboard
├── fitbit/
│   ├── config.py                 # Fitbit API credentials
│   ├── token_manager.py          # OAuth token management
│   ├── get_fitbit_token.py       # Authorization script
│   ├── run_export_ecg.py         # Data export script
│   ├── WebAPI_export.py          # Fitbit API wrapper
│   ├── participants.csv          # Participant registry
│   └── tokens/                   # Per-participant tokens (gitignored)
├── scripts/
│   └── batch_export_all.py       # Batch export for all participants
├── fitbit_exports/                # Data directory (gitignored)
│   ├── ABL01/
│   ├── ABL02/
│   └── ...
├── docs/
│   ├── STUDY_PROTOCOL.md         # Clinical study protocol
│   └── DATA_DICTIONARY.md        # Data field descriptions
├── config/
│   └── .env.example              # Environment variables template
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

---

## 🤝 Contributing

---

## 📄 License

This software is developed for research purposes only. Not for clinical use without IRB approval.

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Status**: Active Development

---

## 🧪 Pilot-Specific Details per Supervisor Guidance

- **Framing**: This is a pilot feasibility cohort at Sunnybrook; initial target enrollment is 20 participants (10 ablation + 10 cardioversion).
- **Intermittent Clinical Monitoring**: References to specific vendors are generalized as “intermittent clinical-grade patch monitoring (e.g., external patch monitor)” at approximately 3 and 6 months.
- **Primary Outcome (clarified)**: Time to AF detection comparing smartwatch and conventional monitoring. We record two timestamps for analysis:
  - Device-detected time: first smartwatch-detected AF event (ECG app or irregular rhythm notification).
  - Clinician-notified time: first documented investigator/clinician notification based on any device/report.
  Both will be captured; analyses may report either or both depending on protocol.
- **Monitoring Responsibility**: The research team reviews the Fitbit dashboard on a regular cadence (e.g., weekly). Treating electrophysiologists may receive summaries as needed per protocol.
- **Acceptability & Equity**: Collect usability and acceptability feedback post-monitoring, including optional equity considerations (e.g., self-reported skin tone as a proxy for PPG-related accuracy considerations).
- **Survey**: See `docs/ACCEPTABILITY_SURVEY.md` for a lightweight post-monitoring survey instrument.

