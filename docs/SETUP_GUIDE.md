# 🚀 Setup Guide - Fitbit Clinical Dashboard

Complete step-by-step instructions for setting up the dashboard for your clinical study.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Fitbit API Configuration](#fitbit-api-configuration)
4. [Participant Enrollment](#participant-enrollment)
5. [First Data Export](#first-data-export)
6. [Dashboard Access](#dashboard-access)
7. [Troubleshooting](#troubleshooting)
8. [Clinical Monitoring Context](#clinical-monitoring-context)
9. [Outcome Definitions](#outcome-definitions)

---

## Prerequisites

### Required Software
- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Git** (for cloning repository)
- **Web browser** (Chrome, Firefox, or Edge)

### Required Accounts
- **Fitbit Developer Account** (dev.fitbit.com)
- **Study email accounts** for each participant
  - Format: `study-abl01@sunnybrook.ca`, `study-cvr01@sunnybrook.ca`, etc.
  - Do NOT use personal Fitbit accounts

### Required Infrastructure
- **Sunnybrook password-protected machine** for data storage
- **No cloud storage** (AWS, Google Cloud, etc.)
- **IRB approval** for clinical study

---

## Initial Setup

### Step 1: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/your-org/fitbit-clinical-dashboard.git
cd fitbit-clinical-dashboard
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 4: Create Data Directories

```bash
# Create required directories
mkdir fitbit_exports
mkdir fitbit/tokens
mkdir logs
mkdir logs/fitbit
```

---

## Fitbit API Configuration

### Step 1: Register Fitbit Application

1. Go to https://dev.fitbit.com/apps
2. Click "Register an App"
3. Fill in details:
   - **Application Name**: "Sunnybrook AFib Clinical Study"
   - **Description**: "Clinical study dashboard for AFib monitoring"
   - **Application Website**: "https://sunnybrook.ca"
   - **Organization**: "Sunnybrook Health Sciences Centre"
   - **Organization Website**: "https://sunnybrook.ca"
   - **OAuth 2.0 Application Type**: "Personal"
   - **Callback URL**: `http://localhost:8080/`
   - **Default Access Type**: "Read-Only"
4. Accept terms and register
5. **Save your Client ID and Client Secret**

### Step 2: Configure Application

```bash
# Copy example config
cp fitbit/config.py.example fitbit/config.py

# Edit config.py with your credentials
nano fitbit/config.py  # or use your preferred editor
```

Update these values in `fitbit/config.py`:
```python
CLIENT_ID = 'YOUR_ACTUAL_CLIENT_ID'
CLIENT_SECRET = 'YOUR_ACTUAL_CLIENT_SECRET'
REDIRECT_URI = 'http://localhost:8080/'
```

**⚠️ SECURITY WARNING:** Never commit `config.py` to Git!

---

## Participant Enrollment

### Step 1: Create Study Email Accounts

For each participant, create a dedicated email account:

**Naming Convention:**
- Ablation arm: `study-abl01@sunnybrook.ca`, `study-abl02@sunnybrook.ca`, etc.
- Cardioversion arm: `study-cvr01@sunnybrook.ca`, `study-cvr02@sunnybrook.ca`, etc.

### Step 2: Register Fitbit Accounts

For each study email:
1. Go to https://www.fitbit.com/signup
2. Register with study email
3. Set strong password (store securely)
4. Complete profile setup
5. Note: Participant will receive physical Fitbit device

### Step 3: Update Participant Registry

```bash
# Copy example registry
cp fitbit/participants.csv.example fitbit/participants.csv

# Edit with actual participant data
nano fitbit/participants.csv
```

Required fields:
- `studyId`: Unique identifier (e.g., ABL01, CVR01)
- `firstName`: Participant first name
- `lastName`: Participant last name
- `phone`: Contact phone number
- `email`: Study email address
- `deviceId`: Fitbit device serial number
- `status`: invited | enrolled | paused | withdrawn | completed
- `startDate`: Study start date (YYYY-MM-DD)
- `endDate`: Expected study end date (YYYY-MM-DD)
- `expectedPerDay`: Target ECGs per day (usually 2)
- `notes`: Any additional notes

### Step 4: Authorize Participant Access

**⚠️ Run this ONLY on secure Sunnybrook machine:**

```bash
# Authorize participant
python fitbit/get_fitbit_token.py --participant ABL01

# Follow the prompts:
# 1. Browser will open to Fitbit login
# 2. Login with study email (study-abl01@sunnybrook.ca)
# 3. Authorize the application
# 4. Copy the code from redirect URL
# 5. Paste into terminal
```

This creates `fitbit/tokens/ABL01.json` with OAuth credentials.

**Repeat for each participant.**

---

## First Data Export

### Single Participant Test

```bash
# Export last 7 days for one participant
python fitbit/run_export_ecg.py \
  2025-10-21 \
  2025-10-28 \
  fitbit_exports/ABL01 \
  ABL01 \
  --cardiac-only \
  --verbose \
  --participant ABL01
```

### Verify Export

```bash
# Check exported files
ls fitbit_exports/ABL01/

# Should see:
# - ECG_summary.csv
# - ECG_waveforms_index.csv
# - ecg_waveforms/ (directory)
# - daily_cardiac_summary.csv
```

### Batch Export All Participants

```bash
# Export last 7 days for all participants
python scripts/batch_export_all.py \
  --days 7 \
  --cardiac-only \
  --verbose

# Check batch summary
cat logs/fitbit/batch_summary_*.json
```

---

## Dashboard Access

### Start Dashboard

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Streamlit dashboard
streamlit run dashboard/app.py --server.port 8502

# Dashboard will open at http://localhost:8502
```

### First Login

1. Dashboard loads automatically in browser
2. Quick Actions bar shows:
   - 🔄 Refresh Data
   - 📥 Batch Export
   - 👥 View Compliance
   - 🔐 Authorize Participant
3. Study Overview shows enrollment progress
4. Navigate tabs:
   - **Waveforms**: View individual ECG recordings
   - **Compliance**: Monitor adherence metrics
   - **Participants**: Manage enrollment

### Daily Workflow

1. **Morning: Check Compliance**
   - View "Study Overview" metrics
   - Check "Active (48h)" count
   - Review "Overall Adherence" percentage

2. **Run Batch Export**
   - Click "📥 Batch Export" button
   - Copy command and run in terminal
   - Or schedule as daily cron job

3. **Review Alerts**
   - Go to "Compliance" tab
   - Check for stale ECG warnings
   - Contact participants with low 7-day rates

4. **Analyze Waveforms** (as needed)
   - Go to "Waveforms" tab
   - Select participant from sidebar
   - Review ECG quality and classifications

---

## Troubleshooting

### Issue: "No module named 'streamlit'"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "Port 8502 already in use"

**Solution:**
```bash
# Use different port
streamlit run dashboard/app.py --server.port 8503
```

### Issue: "No tokens found for participant"

**Solution:**
```bash
# Re-run authorization
python fitbit/get_fitbit_token.py --participant ABL01
```

### Issue: "ECG_summary.csv not found"

**Solution:**
```bash
# Run data export for that participant
python fitbit/run_export_ecg.py \
  2025-10-01 \
  2025-10-28 \
  fitbit_exports/ABL01 \
  ABL01 \
  --participant ABL01
```

### Issue: "Token expired"

**Solution:**
Tokens auto-refresh, but if issues persist:
```bash
# Check token file exists
ls fitbit/tokens/ABL01.json

# If missing, re-authorize
python fitbit/get_fitbit_token.py --participant ABL01
```

### Issue: "Invalid client credentials"

**Solution:**
```bash
# Verify config.py has correct credentials
cat fitbit/config.py

# Ensure CLIENT_ID and CLIENT_SECRET match Fitbit dev portal
```

---

## Clinical Monitoring Context

- This project is framed as a pilot feasibility cohort.
- Intermittent clinical monitoring is generalized as **intermittent clinical-grade patch monitoring** (e.g., external patch monitor) typically around 3 and 6 months. Vendor may vary.
- The research team reviews Fitbit dashboard data on a regular cadence (e.g., weekly) and may provide summaries to treating EP physicians as needed per protocol.

---

## Outcome Definitions

**Primary outcome**: time to AF detection comparing smartwatch and conventional monitoring.

To support analysis flexibility, capture both timestamps when available:
- **Device-detected time**: first smartwatch-detected AF event (Fitbit ECG or irregular rhythm notification).
- **Clinician-notified time**: first investigator/clinician notification based on any device/report.

The operational definition used in the dashboard can be selected in-app (see the “Outcome definitions and monitoring policy” panel).

---

## Security Checklist

Before going live with the study:

- [ ] All participant authorization done on Sunnybrook machines
- [ ] No tokens committed to Git (`fitbit/tokens/` in .gitignore)
- [ ] No participant data committed to Git (`fitbit_exports/` in .gitignore)
- [ ] `config.py` is .gitignored
- [ ] Study email accounts use strong passwords
- [ ] IRB approval obtained
- [ ] Data retention policy documented
- [ ] Backup strategy in place
- [ ] Access logs enabled

---

## Next Steps

1. **Test with pilot participants** (2-3 participants)
2. **Verify data collection** for 1 week
3. **Train study coordinators** on dashboard use
4. **Schedule regular data exports** (daily/weekly)
5. **Set up compliance monitoring** alerts
6. **Document any issues** and solutions
7. **Scale to full enrollment** (20 participants)

---

## Support Contacts

**Technical Issues**: Mithun (Developer)  
**Clinical Questions**: Chris, Alex (PIs)  
**IRB/Ethics**: Study Coordinator  
**IT Infrastructure**: Sunnybrook IT Support

---

**Last Updated**: October 2025  
**Version**: 1.0.0

