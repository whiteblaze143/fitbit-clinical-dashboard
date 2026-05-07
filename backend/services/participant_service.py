import csv
from pathlib import Path
from backend.core.config import PARTICIPANTS_CSV_PATH, FITBIT_EXPORTS_DIR

def read_participants():
    if not PARTICIPANTS_CSV_PATH.exists():
        return []

    participants = []
    with open(PARTICIPANTS_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            participants.append(row)
    return participants

def write_participants(participants):
    if not participants:
        return

    # Ensure directory exists
    PARTICIPANTS_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["studyId", "firstName", "lastName", "phone", "email", "deviceId", "status", "startDate", "endDate", "expectedPerDay", "notes"]

    # Merge dynamically found keys to prevent data loss
    for p in participants:
        for k in p.keys():
            if k not in fieldnames:
                fieldnames.append(k)

    with open(PARTICIPANTS_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in participants:
            writer.writerow(p)

def get_available_participants_exports():
    if not FITBIT_EXPORTS_DIR.exists():
        return []

    participants = []
    for item in FITBIT_EXPORTS_DIR.iterdir():
        if item.is_dir() and item.name != "logs":
            participants.append(item.name)

    if not participants:
        participants = ["default"]

    return participants
