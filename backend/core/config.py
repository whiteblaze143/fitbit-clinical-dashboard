import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Backend specific settings
DATABASE_URL = f"sqlite:///{BASE_DIR}/apps/app_data/dashboard.db"

# Data Directories
FITBIT_EXPORTS_DIR = Path(os.getenv("FITBIT_EXPORTS_DIR", BASE_DIR / "fitbit_exports"))
PARTICIPANTS_CSV_PATH = BASE_DIR / "fitbit" / "participants.csv"

# Make sure apps data dir exists
APP_DATA_DIR = BASE_DIR / "apps" / "app_data"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
