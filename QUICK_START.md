# ⚡ Quick Start - Fitbit Clinical Dashboard

**Get up and running in 5 minutes!**

---

## 1. Clone & Setup

```bash
# Clone repository
git clone https://github.com/your-org/fitbit-clinical-dashboard.git
cd fitbit-clinical-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 2. Configure Fitbit API

```bash
# Copy config template
cp fitbit/config.py.example fitbit/config.py

# Edit with your Fitbit app credentials
# Get credentials from: https://dev.fitbit.com/apps
nano fitbit/config.py
```

Update:
```python
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
```

---

## 3. Add Participants

```bash
# Copy participant registry template
cp fitbit/participants.csv.example fitbit/participants.csv

# Edit with your study participants
nano fitbit/participants.csv
```

---

## 4. Authorize First Participant

**⚠️ Run on secure Sunnybrook machine only!**

```bash
# Create tokens directory
mkdir -p fitbit/tokens

# Authorize participant (example: ABL01)
python fitbit/get_fitbit_token.py --participant ABL01

# Follow prompts to login with study email
```

---

## 5. Export Data

```bash
# Create export directory
mkdir -p fitbit_exports

# Export last 7 days for participant
python fitbit/run_export_ecg.py \
  2025-10-21 2025-10-28 \
  fitbit_exports/ABL01 ABL01 \
  --cardiac-only --verbose --participant ABL01
```

---

## 6. Launch Dashboard

```bash
# Start dashboard
streamlit run dashboard/app.py --server.port 8502

# Opens automatically at: http://localhost:8502
```

---

## 🎉 You're Ready!

Navigate the dashboard:
- **Quick Actions**: Batch export, refresh, authorize
- **Study Overview**: See enrollment progress (X/10 per arm)
- **Waveforms Tab**: Analyze individual ECG recordings
- **Compliance Tab**: Monitor adherence metrics
- **Participants Tab**: Manage enrollment
- **Pilot Context**: The dashboard supports a pilot feasibility study design and generalizes intermittent clinical-grade patch monitoring (e.g., external patch monitor).
- **Acceptability Survey**: After monitoring, capture usability and equity insights. See `docs/ACCEPTABILITY_SURVEY.md`.

---

## Daily Workflow

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Run batch export (all participants)
python scripts/batch_export_all.py --days 7 --cardiac-only --verbose

# 3. Start dashboard
streamlit run dashboard/app.py --server.port 8502

# 4. Review compliance metrics
# 5. Check for alerts
# 6. Contact participants if needed
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | Use `--server.port 8503` |
| No tokens | Run `python fitbit/get_fitbit_token.py --participant <ID>` |
| No data | Run export script for that participant |
| Import error | Check virtual environment is activated |

---

## Need Help?

- **Full documentation**: See `README.md`
- **Setup guide**: See `docs/SETUP_GUIDE.md`
- **Technical support**: Contact Mithun
- **Clinical questions**: Contact Chris or Alex

---

**Version**: 1.0.0  
**Institution**: Sunnybrook Health Sciences Centre

