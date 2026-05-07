import pandas as pd
import json
from backend.core.config import FITBIT_EXPORTS_DIR
from pathlib import Path

def get_summary_df(participant_id=None):
    if participant_id:
        p = FITBIT_EXPORTS_DIR / participant_id / "ECG_summary.csv"
        if p.exists():
            return pd.read_csv(p)
        return pd.DataFrame()
    else:
        # Concatenate all
        dfs = []
        if FITBIT_EXPORTS_DIR.exists():
            for d in FITBIT_EXPORTS_DIR.iterdir():
                if d.is_dir():
                    p = d / "ECG_summary.csv"
                    if p.exists():
                        df = pd.read_csv(p)
                        df['studyId'] = d.name
                        dfs.append(df)
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()

def get_index_df(participant_id=None):
    if participant_id:
        p = FITBIT_EXPORTS_DIR / participant_id / "ECG_waveforms_index.csv"
        if p.exists():
            df = pd.read_csv(p)
            df['studyId'] = participant_id
            return df
        return pd.DataFrame()
    else:
        dfs = []
        if FITBIT_EXPORTS_DIR.exists():
            for d in FITBIT_EXPORTS_DIR.iterdir():
                if d.is_dir():
                    p = d / "ECG_waveforms_index.csv"
                    if p.exists():
                        df = pd.read_csv(p)
                        df['studyId'] = d.name
                        dfs.append(df)
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()

def get_daily_df(participant_id=None):
    if participant_id:
        p = FITBIT_EXPORTS_DIR / participant_id / "daily_cardiac_summary.csv"
        if p.exists():
            df = pd.read_csv(p)
            df['studyId'] = participant_id
            return df
        return pd.DataFrame()
    else:
        dfs = []
        if FITBIT_EXPORTS_DIR.exists():
            for d in FITBIT_EXPORTS_DIR.iterdir():
                if d.is_dir():
                    p = d / "daily_cardiac_summary.csv"
                    if p.exists():
                        df = pd.read_csv(p)
                        df['studyId'] = d.name
                        dfs.append(df)
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()

def get_waveform_data(participant_id, stable_ecg_id, fs=250.0):
    p = FITBIT_EXPORTS_DIR / participant_id / "ecg_waveforms" / f"{stable_ecg_id}.csv"
    if not p.exists():
        # Maybe the index has a different csvPath, fallback to root ecg_waveforms if needed
        p = FITBIT_EXPORTS_DIR / "ecg_waveforms" / f"{stable_ecg_id}.csv"
        if not p.exists():
            return None

    df = pd.read_csv(p)
    return df
