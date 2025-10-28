# 📁 Repository Structure

Complete overview of the Fitbit Clinical Dashboard repository.

---

## Directory Structure

```
fitbit-clinical-dashboard/
│
├── 📱 dashboard/                    # Main Dashboard Application
│   └── app.py                       # Streamlit dashboard (refactored from streamlit_app.py)
│
├── 💓 fitbit/                       # Fitbit API Integration
│   ├── config.py                    # API credentials (DO NOT COMMIT - gitignored)
│   ├── config.py.example            # Template for API configuration
│   ├── get_fitbit_token.py          # OAuth authorization script
│   ├── token_manager.py             # Token storage and refresh logic
│   ├── run_export_ecg.py            # Single participant data export
│   ├── WebAPI_export.py             # Fitbit API wrapper
│   ├── participants.csv             # Participant registry (DO NOT COMMIT - gitignored)
│   ├── participants.csv.example     # Template participant data
│   └── tokens/                      # Per-participant OAuth tokens (gitignored)
│       └── .gitkeep
│
├── 🔧 scripts/                      # Automation Scripts
│   └── batch_export_all.py          # Batch export for all participants
│
├── 📚 docs/                         # Documentation
│   ├── SETUP_GUIDE.md               # Comprehensive setup instructions
│   ├── STUDY_PROTOCOL.md            # Clinical study protocol (to be added)
│   └── DATA_DICTIONARY.md           # Data field descriptions (to be added)
│
├── ⚙️ config/                       # Configuration Files
│   └── .env.example                 # Environment variables template (to be added)
│
├── 📋 README.md                     # Main documentation
├── ⚡ QUICK_START.md                # 5-minute setup guide
├── 📁 REPOSITORY_STRUCTURE.md       # This file
├── 📄 LICENSE                       # MIT License with clinical use terms
├── 📦 requirements.txt              # Python dependencies
└── 🚫 .gitignore                    # Git ignore rules (protects sensitive data)

# Data Directories (Created at runtime, not in repo)
├── fitbit_exports/                  # Exported participant data (gitignored)
│   ├── ABL01/
│   │   ├── ECG_summary.csv
│   │   ├── ECG_waveforms_index.csv
│   │   ├── ecg_waveforms/*.csv
│   │   └── daily_cardiac_summary.csv
│   ├── ABL02/
│   └── ...
│
└── logs/                            # Application logs (gitignored)
    └── fitbit/
        └── batch_summary_*.json
```

---

## Key Files Explained

### Dashboard
- **`dashboard/app.py`**: Main Streamlit application
  - Multi-participant view
  - Study overview metrics (10+10 enrollment tracking)
  - Quick actions bar
  - Three tabs: Waveforms, Compliance, Participants
  - Professional UI with gradient header and styled tabs

### Fitbit Integration
- **`fitbit/config.py`**: Contains Fitbit API credentials
  - ⚠️ **NEVER commit this file** - it's in .gitignore
  - Copy from `config.py.example` and fill in your credentials

- **`fitbit/get_fitbit_token.py`**: OAuth authorization
  - Run once per participant on secure machine
  - Creates `tokens/<participant_id>.json`
  - Usage: `python fitbit/get_fitbit_token.py --participant ABL01`

- **`fitbit/token_manager.py`**: Token management
  - Automatic token refresh
  - Per-participant token storage
  - Secure credential handling

- **`fitbit/run_export_ecg.py`**: Data export
  - Downloads ECG data for date range
  - Saves to `fitbit_exports/<participant_id>/`
  - Usage: `python fitbit/run_export_ecg.py <start> <end> <output> <participant>`

- **`fitbit/WebAPI_export.py`**: Fitbit API wrapper
  - Handles API requests
  - Pagination support
  - Error handling and retry logic

- **`fitbit/participants.csv`**: Participant registry
  - Contains PHI - never commit
  - Fields: studyId, name, contact, dates, device, status
  - Use `participants.csv.example` as template

### Scripts
- **`scripts/batch_export_all.py`**: Batch automation
  - Exports data for all registered participants
  - Reads from `fitbit/participants.csv`
  - Uses per-participant tokens
  - Generates batch summary logs
  - Usage: `python scripts/batch_export_all.py --days 7 --cardiac-only --verbose`

### Documentation
- **`README.md`**: Complete project documentation
  - Overview, features, installation
  - Usage instructions
  - Clinical study information
  - Security and compliance notes

- **`QUICK_START.md`**: Fast setup (5 minutes)
  - Minimal steps to get running
  - Perfect for new team members

- **`docs/SETUP_GUIDE.md`**: Detailed setup
  - Step-by-step instructions
  - Troubleshooting guide
  - Security checklist
  - Daily workflow

### Configuration
- **`requirements.txt`**: Python dependencies
  - streamlit, pandas, numpy, plotly, scipy
  - requests, requests-oauthlib
  - python-dotenv, python-dateutil

- **`.gitignore`**: Protect sensitive data
  - Tokens, credentials, config files
  - Participant data exports
  - Python cache files
  - IDE settings

- **`LICENSE`**: MIT License
  - Open source with clinical use terms
  - Research purposes disclaimer
  - IRB approval requirement

---

## What's NOT in the Repository

### Sensitive Data (Gitignored)
- ✅ `fitbit/config.py` - API credentials
- ✅ `fitbit/tokens/` - OAuth tokens
- ✅ `fitbit/participants.csv` - Participant information
- ✅ `fitbit_exports/` - ECG data exports
- ✅ `logs/` - Application logs

### Templates Provided
- ✅ `fitbit/config.py.example` - Config template
- ✅ `fitbit/participants.csv.example` - Registry template

### Why This Matters
- **Security**: No credentials in Git history
- **Privacy**: No PHI exposed
- **Compliance**: HIPAA-compliant data handling
- **Portability**: Easy to clone and setup on different machines

---

## File Size Estimates

| Directory | Typical Size | Notes |
|-----------|--------------|-------|
| `dashboard/` | ~100 KB | Single Python file |
| `fitbit/` | ~50 KB | Scripts only (no data) |
| `scripts/` | ~10 KB | Automation scripts |
| `docs/` | ~50 KB | Markdown documentation |
| `requirements.txt` | ~1 KB | Dependency list |
| **Total (repo)** | **~250 KB** | Lightweight and portable |
| `fitbit_exports/` | **~100 MB - 1 GB** | Per participant, not in repo |
| `fitbit/tokens/` | **~10 KB** | Per participant, not in repo |

---

## How to Share This Repository

### With Alex and Chris

```bash
# 1. Initialize git (if not already done)
cd fitbit-clinical-dashboard
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit: Fitbit Clinical Dashboard v1.0"

# 4. Create GitHub repository (on GitHub.com)
# Name: fitbit-clinical-dashboard
# Description: Multi-participant AFib monitoring dashboard
# Private repository recommended

# 5. Add remote and push
git remote add origin https://github.com/your-org/fitbit-clinical-dashboard.git
git branch -M main
git push -u origin main

# 6. Share repository URL with Alex and Chris
```

### They Clone and Setup

```bash
# Clone
git clone https://github.com/your-org/fitbit-clinical-dashboard.git
cd fitbit-clinical-dashboard

# Follow QUICK_START.md
# Takes 5 minutes to get running
```

---

## Maintenance

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes
3. Test thoroughly
4. Commit: `git commit -m "Add: description"`
5. Push: `git push origin feature/new-feature`
6. Create pull request

### Updating Documentation
- Update `README.md` for major changes
- Update `QUICK_START.md` if setup process changes
- Update `docs/SETUP_GUIDE.md` for detailed instructions
- Keep version numbers consistent

### Security Updates
- Regularly review `.gitignore`
- Audit for accidentally committed credentials
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review access logs

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Oct 2025 | Initial release with multi-participant support |

---

## Contact

**Maintainer**: Mithun (Developer)  
**Principal Investigators**: Chris, Alex  
**Institution**: Sunnybrook Health Sciences Centre

---

**Last Updated**: October 2025

