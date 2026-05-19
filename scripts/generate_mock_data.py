import os
import csv
import json
import math
import random
from pathlib import Path
import numpy as np

# Setup directories
BASE_DIR = Path(__file__).resolve().parent.parent
FITBIT_EXPORTS_DIR = BASE_DIR / "fitbit_exports"
FITBIT_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

participants = [
    {"studyId": "ABL01", "name": "John Doe", "status": "enrolled", "start_days_ago": 15},
    {"studyId": "ABL02", "name": "Jane Smith", "status": "enrolled", "start_days_ago": 10},
    {"studyId": "CVR01", "name": "Bob Johnson", "status": "enrolled", "start_days_ago": 12},
    {"studyId": "CVR02", "name": "Alice Williams", "status": "invited", "start_days_ago": 0}
]

def generate_ecg_waveform(fs=250.0, duration=30.0, hr=72.0):
    """Generates a highly realistic synthetic ECG signal with standard P-Q-R-S-T waves"""
    n_samples = int(fs * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    
    # Baseline drift (low freq breathing cycle)
    baseline = 0.1 * np.sin(2 * np.pi * 0.15 * t)
    
    # High frequency muscle noise
    noise = 0.015 * np.random.normal(size=n_samples)
    
    # 60 Hz powerline interference (very subtle)
    interference = 0.005 * np.sin(2 * np.pi * 60 * t)
    
    # Initialize ECG signal
    ecg = baseline + noise + interference
    
    # Heartbeat timing
    rr_interval = 60.0 / hr
    # Add minor heart rate variability (HRV)
    heartbeat_times = []
    curr_time = 0.2
    while curr_time < duration - 0.6:
        heartbeat_times.append(curr_time)
        # Add random variation to RR interval
        curr_time += rr_interval + random.uniform(-0.04, 0.04)
        
    for h_time in heartbeat_times:
        # Relative time from start of this beat
        t_rel = t - h_time
        
        # P-wave
        p = 0.12 * np.exp(-((t_rel - 0.08) / 0.025)**2)
        # Q-wave
        q = -0.15 * np.exp(-((t_rel - 0.14) / 0.012)**2)
        # R-wave (Main QRS Spike)
        r = 1.3 * np.exp(-((t_rel - 0.16) / 0.008)**2)
        # S-wave
        s = -0.28 * np.exp(-((t_rel - 0.18) / 0.012)**2)
        # T-wave
        t_wave = 0.35 * np.exp(-((t_rel - 0.32) / 0.05)**2)
        
        # Sum components
        ecg += p + q + r + s + t_wave
        
    return t, ecg

def create_mock_data():
    print("Generating clinical mock data...")
    
    for p in participants:
        if p["status"] == "invited":
            continue
            
        pid = p["studyId"]
        p_dir = FITBIT_EXPORTS_DIR / pid
        wave_dir = p_dir / "ecg_waveforms"
        wave_dir.mkdir(parents=True, exist_ok=True)
        
        # We'll generate data for the last start_days_ago days
        summary_records = []
        index_records = []
        daily_records = []
        
        # Random parameters for this patient
        base_hr = random.uniform(62, 78)
        base_hrv = random.uniform(35, 55)
        base_br = random.uniform(12, 16)
        base_spo2 = random.uniform(96.5, 98.8)
        
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=p["start_days_ago"])
        
        for day in range(p["start_days_ago"]):
            curr_date = start_date + timedelta(days=day)
            date_str = curr_date.strftime("%Y-%m-%d")
            
            # 1. Daily summaries
            # Resting HR
            daily_records.append({
                "date": date_str,
                "metric": "HR_summary",
                "value": json.dumps({"restingHeartRate": round(base_hr + random.uniform(-3, 3), 1)})
            })
            # HRV (RMSSD)
            daily_records.append({
                "date": date_str,
                "metric": "HRV",
                "value": json.dumps({"dailyRmssd": round(base_hrv + random.uniform(-5, 5), 1)})
            })
            # Breathing rate (RR)
            daily_records.append({
                "date": date_str,
                "metric": "RR",
                "value": json.dumps({"breathingRate": round(base_br + random.uniform(-1, 1), 1)})
            })
            # SpO2
            daily_records.append({
                "date": date_str,
                "metric": "SpO2",
                "value": json.dumps({"avg": round(base_spo2 + random.uniform(-0.8, 0.8), 1)})
            })
            
            # 2. ECGs (usually 1-2 per day)
            n_ecgs = random.choice([1, 2, 2]) # Higher chance of 2 for adherence compliance
            for ecg_idx in range(n_ecgs):
                stable_id = f"ecg_{pid}_{curr_date.strftime('%Y%m%d')}_{ecg_idx+1}"
                time_str = f"{date_str}T{10 + ecg_idx * 4:02d}:30:00"
                
                # Check for standard classifications: NormalSinusRhythm, AtrialFibrillation, Inconclusive
                classification = "NormalSinusRhythm"
                # CVR patients might have AtrialFibrillation occasional recurrence
                if pid == "CVR01" and day in [4, 9]:
                    classification = "AtrialFibrillation"
                elif pid == "ABL02" and day == 6:
                    classification = "Inconclusive"
                
                hr_for_ecg = base_hr + random.uniform(-5, 15)
                if classification == "AtrialFibrillation":
                    hr_for_ecg = base_hr + random.uniform(25, 45) # elevated heart rate during AF
                    
                # Generate waveform CSV
                t_arr, v_arr = generate_ecg_waveform(fs=250.0, duration=30.0, hr=hr_for_ecg)
                wave_csv_path = wave_dir / f"{stable_id}.csv"
                with open(wave_csv_path, "w", newline="") as wf:
                    writer = csv.writer(wf)
                    writer.writerow(["timeSec", "mV"])
                    for t_val, v_val in zip(t_arr, v_arr):
                        writer.writerow([round(t_val, 4), round(v_val, 5)])
                
                # Append to summary
                summary_records.append({
                    "stableEcgId": stable_id,
                    "startTime": time_str,
                    "classification": classification,
                    "averageHeartRate": round(hr_for_ecg),
                    "deviceName": "Sense 2",
                    "firmwareVersion": "60.20001.194.86"
                })
                
                # Append to index
                index_records.append({
                    "stableEcgId": stable_id,
                    "startTime": time_str,
                    "classification": classification,
                    "samplingFrequency": 250.0,
                    "scalingFactor": 0.012,
                    "leadNumber": 1,
                    "csvPath": f"ecg_waveforms/{stable_id}.csv"
                })
                
        # Write summaries
        with open(p_dir / "ECG_summary.csv", "w", newline="") as sf:
            writer = csv.DictWriter(sf, fieldnames=["stableEcgId", "startTime", "classification", "averageHeartRate", "deviceName", "firmwareVersion"])
            writer.writeheader()
            for rec in summary_records:
                writer.writerow(rec)
                
        with open(p_dir / "ECG_waveforms_index.csv", "w", newline="") as idx_f:
            writer = csv.DictWriter(idx_f, fieldnames=["stableEcgId", "startTime", "classification", "samplingFrequency", "scalingFactor", "leadNumber", "csvPath"])
            writer.writeheader()
            for rec in index_records:
                writer.writerow(rec)
                
        with open(p_dir / "daily_cardiac_summary.csv", "w", newline="") as df:
            writer = csv.DictWriter(df, fieldnames=["date", "metric", "value"])
            writer.writeheader()
            for rec in daily_records:
                writer.writerow(rec)
                
        print(f"Generated {len(summary_records)} ECG records for participant {pid}.")
        
    print("Mock data generated successfully in fitbit_exports/.")

if __name__ == "__main__":
    create_mock_data()
