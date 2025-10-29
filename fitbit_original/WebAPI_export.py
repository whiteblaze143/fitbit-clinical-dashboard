# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 15:46:11 2023

@author: Jansen Zhou

Updated and Refined by July 29th 2025
@author: Mithun Manivannan 
"""

import requests
import os
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import argparse
import time
import zipfile

def get_with_retry(url: str, headers: dict, max_retries: int = 3, backoff: float = 2.0):
    """GET with simple retry/backoff for 429/5xx."""
    attempt = 0
    while True:
        attempt += 1
        resp = requests.get(url, headers=headers)
        if resp.status_code == 429 or 500 <= resp.status_code < 600:
            if attempt >= max_retries:
                return resp.json() if 'application/json' in resp.headers.get('Content-Type', '') else {"status": resp.status_code, "text": resp.text}
            retry_after = resp.headers.get('Retry-After')
            delay = float(retry_after) if retry_after else backoff * attempt
            time.sleep(delay)
            continue
        try:
            return resp.json()
        except Exception:
            return {"status": resp.status_code, "text": resp.text}

# Create parser
parser = argparse.ArgumentParser(description="Info to send to FitBit Web API")

# Add arguments
parser.add_argument("user", type=str, help="Fitbit user ID (or '-' for the authorized user)")
parser.add_argument("startDate", type=str, help="Start of study period: Format as YYYY-mm-dd")
parser.add_argument("endDate", type=str, help="End of study period: Format as YYYY-mm-dd")
parser.add_argument("Folder", type=str, help="Output folder path for JSON exports")
parser.add_argument("AccessToken", type=str, help="Access Token with required scopes (heartrate, electrocardiogram, profile, etc.)")
parser.add_argument("--cardiac-only", action="store_true", help="Fetch only cardiac-relevant endpoints (ECG, HR, HRV, SpO2, RR)")
parser.add_argument("--verbose", action="store_true", help="Print progress messages")

# Parse arguments
args = parser.parse_args()

# Convert string to datetime.date
startdate = datetime.strptime(args.startDate, "%Y-%m-%d").date()
enddate = datetime.strptime(args.endDate, "%Y-%m-%d").date()
access_token = args.AccessToken
user = args.user

# In[1]:    
    
#Patient parameters to change
# Save path (create if missing)
base = Path(args.Folder)
base.mkdir(parents=True, exist_ok=True)
daterange = pd.date_range(start=startdate, end=enddate)

HR_intraday_total = []
Daily_activity_summary_total = []
Calories_intraday_total = []
Distance_intraday_total = []
Elevation_intraday_total = []
Floors_intraday_total = []
Steps_intraday_total = []

# In[2]:

#get API data specified by uri
header = {'Authorization' : 'Bearer {}'.format(access_token)}

"""Pre-initialize non-cardiac variables to avoid unbound references when --cardiac-only is used."""
AZM_summary = {}
Activity_goals_daily = {}
Activity_goals_weekly = {}
Activity_log_list = {}
Activity_types = {}
Lifetime_stats = {}
Calories_time_series = {}
Distance_time_series = {}
Elevation_time_series = {}
Floors_time_series = {}
Steps_time_series = {}
activityCalories_time_series = {}
caloriesBMR_time_series = {}
minutesSedentary_time_series = {}
minutesLightlyActive_time_series = {}
minutesFairlyActive_time_series = {}
minutesVeryActive_time_series = {}
Devices = {}

if not args.cardiac_only:
    # activity data
    AZM_summary = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/active-zone-minutes/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    Activity_goals_daily = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/goals/daily.json'.format(user=user), header)
    Activity_goals_weekly = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/goals/weekly.json'.format(user=user), header)
    Activity_log_list = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/list.json?afterDate={startdate}&sort=asc&offset=0&limit=100'.format(user=user, startdate=startdate), header)
    Activity_types = get_with_retry('https://api.fitbit.com/1/activities.json', header)
    Lifetime_stats = get_with_retry('https://api.fitbit.com/1/user/{user}/activities.json'.format(user=user), header)
    # devices
    Devices = get_with_retry('https://api.fitbit.com/1/user/{user}/devices.json'.format(user=user), header)

    Calories_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/calories/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    Distance_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/distance/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    Elevation_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/elevation/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    Floors_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/floors/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    Steps_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/steps/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)

    activityCalories_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/activityCalories/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    caloriesBMR_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/caloriesBMR/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    minutesSedentary_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/minutesSedentary/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    minutesLightlyActive_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/minutesLightlyActive/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    minutesFairlyActive_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/minutesFairlyActive/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    minutesVeryActive_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/minutesVeryActive/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)

#body data
#Body_goals_weight = requests.get('https://api.fitbit.com/1/user/{user}/body/log/weight/goal.json'.format(user=user), headers=header).json() #1 request
#Body_goals_fat = requests.get('https://api.fitbit.com/1/user/{user}/body/log/fat/goal.json'.format(user=user), headers=header).json() #1 request
#Body_time_series_bmi = requests.get('https://api.fitbit.com/1/user/{user}/body/bmi/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), headers=header).json() #1 request
#Body_time_series_fat = requests.get('https://api.fitbit.com/1/user/{user}/body/fat/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), headers=header).json() #1 request
#Body_time_series_weight = requests.get('https://api.fitbit.com/1/user/{user}/body/weight/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), headers=header).json() #1 request
#Weight_time_series = requests.get('https://api.fitbit.com/1/user/{user}/body/log/weight/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), headers=header).json() #1 request
    
#RR and VO2 data
RR_summary = get_with_retry('https://api.fitbit.com/1/user/{user}/br/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
# Irregular Rhythm Notifications (if scope enabled); some tenants may not have this
IRN_notifications = {}
try:
    IRN_notifications = get_with_retry('https://api.fitbit.com/1/user/{user}/irregular-heartbeat-notifications/list.json?afterDate={startdate}&sort=asc&offset=0&limit=100'.format(user=user, startdate=startdate), header)
except Exception:
    IRN_notifications = {}
#VO2_summary = requests.get('https://api.fitbit.com/1/user/{user}/cardioscore/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), headers=header).json() #1 request

# Heart data
# ECG list + per-recording fetch (requires 'electrocardiogram' scope; handle if unavailable)
ECG_log_list = {"error": "not requested"}
ECG_recordings = []
try:
    if args.verbose:
        print("Fetching ECG log list using pagination.next (limit<=10, offset=0)...")
    ecg_all = []
    # Per docs: offset is only supported at 0. Use pagination.next to advance.
    url = 'https://api.fitbit.com/1/user/{user}/ecg/list.json?afterDate={startdate}&sort=asc&limit={limit}&offset=0'.format(user=user, startdate=startdate, limit=10)
    seen_urls = set()
    pages = 0
    while isinstance(url, str) and url:
        if url in seen_urls:
            # Prevent accidental loops if API returns the same next link
            break
        seen_urls.add(url)
        page = get_with_retry(url, header)
        pages += 1
        readings = page.get('ecgReadings', []) if isinstance(page, dict) else []
        if readings:
            ecg_all.extend(readings)
        # Read next link per spec
        next_url = None
        if isinstance(page, dict):
            pg = page.get('pagination') or {}
            next_url = pg.get('next')
        url = next_url
        # Safety caps
        if pages >= 200 or len(ecg_all) >= 2000:
            break
    # Consolidated ECG list
    if ecg_all:
        ECG_log_list = {"ecgReadings": ecg_all}

    # Fetch each ECG waveform by ecgId (rate-limit friendly)
    if isinstance(ECG_log_list, dict) and 'ecgReadings' in ECG_log_list:
        for reading in ECG_log_list['ecgReadings']:
            if not isinstance(reading, dict):
                continue
            ecg_id = reading.get('ecgId')
            if not ecg_id:
                continue
            try:
                if args.verbose:
                    print(f"Fetching ECG detail {ecg_id}...")
                ecg_detail = get_with_retry(f'https://api.fitbit.com/1/user/{user}/ecg/{ecg_id}.json', header)
                ECG_recordings.append(ecg_detail)
            except Exception as e:
                ECG_recordings.append({"ecgId": ecg_id, "error": str(e)})
            time.sleep(1)
except Exception as e:
    ECG_log_list = {"error": str(e)}

# Write a CSV summary for ECG metadata
try:
    ecg_rows = []
    readings = ECG_log_list.get('ecgReadings', []) if isinstance(ECG_log_list, dict) else []
    details_by_id = {}
    for d in ECG_recordings:
        # Attempt to index by ecgId where available
        eid = None
        if isinstance(d, dict):
            eid = d.get('ecgId') or d.get('readingId') or d.get('id')
        if eid is not None:
            details_by_id[str(eid)] = d

    import hashlib
    for idx, r in enumerate(readings):
        if not isinstance(r, dict):
            continue
        eid_val = r.get('ecgId')
        eid = str(eid_val) if eid_val is not None else None
        ts = r.get('startTime') or r.get('startDateTime') or r.get('timestamp')
        # Fitbit list payload uses 'resultClassification'
        label = r.get('classification') or r.get('resultClassification') or r.get('label')
        # Derive duration from samples if needed
        dur = r.get('durationSeconds') or r.get('duration')
        if dur is None:
            try:
                sf = r.get('samplingFrequencyHz')
                # Parse sampling frequency if provided as string
                if isinstance(sf, str):
                    try:
                        sf = float(sf)
                    except Exception:
                        sf = None
                samples = r.get('waveformSamples')
                if isinstance(sf, (int, float)) and isinstance(samples, list) and sf:
                    dur = round(len(samples) / float(sf), 3)
            except Exception:
                pass
        detail = details_by_id.get(eid, {}) if eid is not None else {}
        # Common fields to extract (best-effort)
        sampling = None
        leads = None
        avg_hr = r.get('averageHeartRate')
        scaling_factor = r.get('scalingFactor')
        n_samples = r.get('numberOfWaveformSamples')
        device_name = r.get('deviceName')
        firmware_version = r.get('firmwareVersion')
        lead_number = r.get('leadNumber')
        feature_version = r.get('featureVersion')
        if isinstance(detail, dict):
            meta = detail.get('metadata') or {}
            sampling = meta.get('samplingFrequency') or detail.get('samplingFrequency') or sampling
            leads = meta.get('leads') or detail.get('leads') or leads
            avg_hr = detail.get('averageHeartRate') or avg_hr
            scaling_factor = detail.get('scalingFactor') or scaling_factor
            n_samples = detail.get('numberOfWaveformSamples') or n_samples
            device_name = detail.get('deviceName') or device_name
            firmware_version = detail.get('firmwareVersion') or firmware_version
            lead_number = detail.get('leadNumber') or lead_number
            feature_version = detail.get('featureVersion') or feature_version
        # Fallback to list-level sampling if detail missing
        if sampling is None:
            sampling = r.get('samplingFrequencyHz')
        # Normalize numeric types
        try:
            if isinstance(sampling, str):
                sampling = float(sampling)
        except Exception:
            pass
        try:
            if isinstance(scaling_factor, str):
                scaling_factor = float(scaling_factor)
        except Exception:
            pass
        try:
            if isinstance(lead_number, str):
                lead_number = int(lead_number)
        except Exception:
            pass
        # Derive numberOfWaveformSamples if possible
        if n_samples is None:
            wf = r.get('waveformSamples')
            if isinstance(wf, list):
                n_samples = len(wf)

        # Create a stable surrogate ID when Fitbit doesn't provide one
        stable_src = str(ts) + '|' + str(r.get('waveformSamples', [])[:200])
        stable_ecg_id = hashlib.sha1(stable_src.encode('utf-8', errors='ignore')).hexdigest()[:16]

        ecg_rows.append({
            'ecgId': eid if eid is not None else stable_ecg_id,
            'stableEcgId': stable_ecg_id,
            'startTime': ts,
            'classification': label,
            'averageHeartRate': avg_hr,
            'durationSeconds': dur,
            'samplingFrequency': sampling,
            'numberOfWaveformSamples': n_samples,
            'scalingFactor': scaling_factor,
            'leadNumber': lead_number,
            'deviceName': device_name,
            'firmwareVersion': firmware_version,
            'featureVersion': feature_version,
            'leads': leads
        })
    if ecg_rows:
        import csv
        csv_path = base / 'ECG_summary.csv'
        with csv_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(ecg_rows[0].keys()))
            writer.writeheader()
            writer.writerows(ecg_rows)
        if args.verbose:
            print(f"Wrote {csv_path}")
        # Also export individual waveform CSVs and an index for dashboard
        wave_dir = base / 'ecg_waveforms'
        wave_dir.mkdir(parents=True, exist_ok=True)
        idx_rows = []

        # Lookups by startTime and by ecgId from list and details
        readings_by_ts = {}
        for r in readings:
            if isinstance(r, dict):
                ts_r = r.get('startTime') or r.get('startDateTime') or r.get('timestamp')
                if ts_r:
                    readings_by_ts[str(ts_r)] = r

        details_by_eid = {}
        for d in ECG_recordings:
            if isinstance(d, dict):
                deid = d.get('ecgId') or d.get('readingId') or d.get('id')
                if deid is not None:
                    details_by_eid[str(deid)] = d

        def extract_samples_and_fs(list_entry: dict, detail_entry: dict):
            # Prefer list entry if it already contains waveformSamples
            samples = None
            fs = None
            scale = None
            if isinstance(list_entry, dict):
                samples = list_entry.get('waveformSamples')
                fs = list_entry.get('samplingFrequencyHz')
                scale = list_entry.get('scalingFactor')
            if not (isinstance(samples, list) and isinstance(fs, (int, float)) and fs):
                if isinstance(detail_entry, dict):
                    # Check common keys in detail
                    samples = detail_entry.get('waveformSamples') or detail_entry.get('samples')
                    fs = (
                        detail_entry.get('samplingFrequencyHz')
                        or detail_entry.get('samplingFrequency')
                        or (detail_entry.get('metadata') or {}).get('samplingFrequency')
                    )
                    if scale is None:
                        scale = detail_entry.get('scalingFactor') or (detail_entry.get('metadata') or {}).get('scalingFactor')
            # Normalize types
            try:
                if isinstance(fs, str):
                    fs = float(fs)
            except Exception:
                pass
            try:
                if isinstance(scale, str):
                    scale = float(scale)
            except Exception:
                pass
            return samples, fs, scale

        exported = 0
        for row in ecg_rows:
            ts_r = row.get('startTime')
            eid_r = row.get('ecgId')
            list_entry = readings_by_ts.get(str(ts_r), {}) if ts_r else {}
            detail_entry = details_by_eid.get(str(eid_r), {}) if eid_r else {}

            samples, fs, scale = extract_samples_and_fs(list_entry, detail_entry)
            if isinstance(samples, list) and isinstance(fs, (int, float)) and fs:
                sid = row.get('stableEcgId') or row.get('ecgId')
                out_csv = wave_dir / f"{sid}.csv"
                # Write time,value rows
                with out_csv.open('w', newline='', encoding='utf-8') as wf:
                    w = csv.writer(wf)
                    w.writerow(["timeSec", "value", "mV"])
                    # Default scaling per docs if absent
                    sf = scale if isinstance(scale, (int, float)) and scale else 10922
                    inv_sf = 1.0/float(sf) if sf else 0.0
                    for i, v in enumerate(samples):
                        try:
                            mv = float(v) * inv_sf
                        except Exception:
                            mv = ""
                        w.writerow([round(i/float(fs), 6), v, mv])
                idx_rows.append({
                    'stableEcgId': sid,
                    'startTime': ts_r,
                    'samplingFrequency': fs,
                    'durationSeconds': row.get('durationSeconds'),
                    'classification': row.get('classification'),
                    'scalingFactor': scale if scale is not None else 10922,
                    'csvPath': str(out_csv.relative_to(base))
                })
                exported += 1
        if idx_rows:
            idx_path = base / 'ECG_waveforms_index.csv'
            with idx_path.open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list(idx_rows[0].keys()))
                writer.writeheader()
                writer.writerows(idx_rows)
            if args.verbose:
                print(f"Wrote {idx_path} and {exported} waveform CSV(s)")
        elif args.verbose:
            print("No waveform CSVs exported (no samples+Fs present in list or details)")

        # Write an ECG coverage report (JSON)
        try:
            cov = {}
            cov['summary_rows'] = len(ecg_rows)
            cov['waveform_index_rows'] = len(idx_rows)
            cov['waveform_ratio'] = float(len(idx_rows)) / float(len(ecg_rows)) if ecg_rows else 0.0
            # classification counts
            try:
                cls = pd.DataFrame(ecg_rows)['classification'].fillna('NA').value_counts().to_dict()
            except Exception:
                cls = {}
            cov['classification_counts'] = cls
            # Fs distribution
            try:
                fs_vals = [r.get('samplingFrequency') for r in ecg_rows if isinstance(r.get('samplingFrequency'), (int, float))]
                cov['fs_distribution'] = {str(k): int(v) for k, v in pd.Series(fs_vals).value_counts().to_dict().items()}
            except Exception:
                cov['fs_distribution'] = {}
            # anomalies
            cov['anomalies'] = {
                'missing_waveformSamples_in_list': int(sum(1 for r in readings if not isinstance(r.get('waveformSamples'), list))) if isinstance(readings, list) else None,
                'missing_samplingFrequency_in_summary': int(sum(1 for r in ecg_rows if not isinstance(r.get('samplingFrequency'), (int, float))))
            }
            (base / 'ECG_coverage.json').write_text(json.dumps(cov, indent=2))
            if args.verbose:
                print(f"Wrote {(base / 'ECG_coverage.json')}")
        except Exception as _e:
            if args.verbose:
                print('Failed to write ECG_coverage.json:', _e)
except Exception as e:
    if args.verbose:
        print("Failed to write ECG_summary.csv:", e)

HR_time_series = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/heart/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
# Try denser HR intraday (1s) when available; fallback handled in per-day loop
try:
    HR_intraday_1s = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/heart/date/{startdate}/{enddate}/1sec.json'.format(user=user, startdate=startdate, enddate=enddate), header)
except Exception:
    HR_intraday_1s = {}
HRV_summary = get_with_retry('https://api.fitbit.com/1/user/{user}/hrv/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
    
#Sleep data
Sleep_goal = get_with_retry('https://api.fitbit.com/1.2/user/{user}/sleep/goal.json'.format(user=user), header)
Sleep_log = get_with_retry('https://api.fitbit.com/1.2/user/{user}/sleep/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)
Sleep_log_list = get_with_retry('https://api.fitbit.com/1.2/user/{user}/sleep/list.json?afterDate={startdate}&sort=asc&offset=0&limit=100'.format(user=user, startdate=startdate), header)

#Oxygen saturation data
SpO2_summary = get_with_retry('https://api.fitbit.com/1/user/{user}/spo2/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), header)

# Write a compact daily cardiac CSV (best-effort, schema depends on Fitbit)
try:
    import csv
    rows = []
    # Safely reference datasets (if not fetched, default to {})
    _hr_ts = HR_time_series if isinstance(HR_time_series, dict) else {}
    _hrv_sum = HRV_summary if isinstance(HRV_summary, dict) else {}
    _spo2_sum = SpO2_summary if isinstance(SpO2_summary, dict) else {}
    _rr_sum = RR_summary if isinstance(RR_summary, dict) else {}

    # HR daily
    # HR_time_series structure: {'activities-heart': [{'dateTime': 'YYYY-MM-DD', 'value': {...}}], ...}
    for item in _hr_ts.get('activities-heart', []) or []:
        dt = item.get('dateTime') if isinstance(item, dict) else None
        rows.append({'date': dt, 'metric': 'HR_summary', 'value': item.get('value') if isinstance(item, dict) else None})
    # HRV daily
    for d in _hrv_sum.get('hrv', []) or []:
        dt = d.get('dateTime') if isinstance(d, dict) else None
        # Example fields: 'dailyRmssd', 'deepRmssd' vary by API version
        rows.append({'date': dt, 'metric': 'HRV', 'value': d})
    # SpO2 daily
    for d in _spo2_sum.get('spo2', []) or []:
        dt = d.get('dateTime') if isinstance(d, dict) else None
        rows.append({'date': dt, 'metric': 'SpO2', 'value': d})
    # Respiratory Rate daily
    for d in _rr_sum.get('br', []) or []:
        dt = d.get('dateTime') if isinstance(d, dict) else None
        rows.append({'date': dt, 'metric': 'RR', 'value': d})

    if rows:
        csv_path = base / 'daily_cardiac_summary.csv'
        # Flatten value as JSON string to preserve structure
        for r in rows:
            if not isinstance(r.get('value'), (str, int, float)):
                import json as _json
                r['value'] = _json.dumps(r.get('value'))
        with csv_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'metric', 'value'])
            writer.writeheader()
            writer.writerows(rows)
        if args.verbose:
            print(f"Wrote {csv_path}")
except Exception as e:
    if args.verbose:
        print("Failed to write daily_cardiac_summary.csv:", e)
    
#Temperature data
#Temp_core = requests.get('https://api.fitbit.com/1/user/{user}/temp/core/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), headers=header).json() #1 request
#Temp_skin = requests.get('https://api.fitbit.com/1/user/{user}/temp/skin/date/{startdate}/{enddate}.json'.format(user=user, startdate=startdate, enddate=enddate), headers=header).json() #1 request

#intraday data
#AZM_intraday = requests.get('https://api.fitbit.com/1/user/{user}/activities/active-zone-minutes/date/{startdate}/{enddate}/1min.json'.format(user=user, startdate=startdate, enddate=enddate), headers=header).json() #1 request
RR_intraday = get_with_retry('https://api.fitbit.com/1/user/{user}/br/date/{startdate}/{enddate}/all.json'.format(user=user, startdate=startdate, enddate=enddate), header)
HRV_intraday = get_with_retry('https://api.fitbit.com/1/user/{user}/hrv/date/{startdate}/{enddate}/all.json'.format(user=user, startdate=startdate, enddate=enddate), header)
SpO2_intraday = get_with_retry('https://api.fitbit.com/1/user/{user}/spo2/date/{startdate}/{enddate}/all.json'.format(user=user, startdate=startdate, enddate=enddate), header)

for date in daterange:
    # Always fetch HR intraday (cardiac)
    HR_intraday = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/heart/date/{date}/1d/1min.json'.format(user=user, date=date.strftime("%Y-%m-%d")), header) # 1 request per day
    HR_intraday_total.append(HR_intraday)
    # Daily activity summary is non-cardiac; include only when not in cardiac-only mode
    if not args.cardiac_only:
        Daily_activity_summary = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/date/{date}.json'.format(user=user, date=date.strftime("%Y-%m-%d")), header)
        Daily_activity_summary_total.append(Daily_activity_summary)
    #Body_fat_log = requests.get('https://api.fitbit.com/1/user/{user}/body/log/fat/date/{date}.json'.format(user=user, date=date.strftime("%Y-%m-%d")), headers=header).json() #28 requests
    #Weight_log = requests.get('https://api.fitbit.com/1/user/{user}/body/log/weight/date/{date}.json'.format(user=user, date=date.strftime("%Y-%m-%d")), headers=header).json() #28 requests


# Only pause and fetch non-cardiac intraday metrics when not in cardiac-only mode
if not args.cardiac_only:
    # Allow configuring the pause to be gentle with rate limits (default 600s)
    try:
        pause_sec = float(os.getenv('FITBIT_NONCARDIAC_PAUSE_SEC', '600'))
    except Exception:
        pause_sec = 600.0
    time.sleep(pause_sec)
        
if not args.cardiac_only:
    for date in daterange:
        Calories_intraday = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/calories/date/{date}/1d/1min.json'.format(user=user, date=date.strftime("%Y-%m-%d")), header)
        Calories_intraday_total.append(Calories_intraday)
        Distance_intraday = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/distance/date/{date}/1d/1min.json'.format(user=user, date=date.strftime("%Y-%m-%d")), header)
        Distance_intraday_total.append(Distance_intraday)
        Elevation_intraday = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/elevation/date/{date}/1d/1min.json'.format(user=user, date=date.strftime("%Y-%m-%d")), header)
        Elevation_intraday_total.append(Elevation_intraday)
        Floors_intraday = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/floors/date/{date}/1d/1min.json'.format(user=user, date=date.strftime("%Y-%m-%d")), header)
        Floors_intraday_total.append(Floors_intraday)
        Steps_intraday = get_with_retry('https://api.fitbit.com/1/user/{user}/activities/steps/date/{date}/1d/1min.json'.format(user=user, date=date.strftime("%Y-%m-%d")), header)
        Steps_intraday_total.append(Steps_intraday)
                    
filenames = ("AZM_summary","Activity_goals_daily","Activity_goals_weekly","Activity_log_list","Activity_types","Lifetime_stats",
                      "Calories_time_series","Distance_time_series","Elevation_time_series","Floors_time_series","Steps_time_series",
                      "activityCalories_time_series","caloriesBMR_time_series","minutesSedentary_time_series","minutesLightlyActive_time_series","minutesFairlyActive_time_series","minutesVeryActive_time_series",
                      "RR_summary","IRN_notifications",
                      "HR_time_series","HRV_summary",
                      "ECG_log_list","ECG_recordings",
                      "Sleep_goal","Sleep_log","Sleep_log_list",
                      "SpO2_summary",
                      "RR_intraday","HRV_intraday","SpO2_intraday","HR_intraday_1s",
                      "HR_intraday","Daily_activity_summary",
                      "Calories_intraday","Distance_intraday","Elevation_intraday","Floors_intraday","Steps_intraday")

filelist = np.array([AZM_summary,Activity_goals_daily,Activity_goals_weekly,Activity_log_list,Activity_types,Lifetime_stats,
                      Calories_time_series,Distance_time_series,Elevation_time_series,Floors_time_series,Steps_time_series,
                      activityCalories_time_series,caloriesBMR_time_series,minutesSedentary_time_series,minutesLightlyActive_time_series,minutesFairlyActive_time_series,minutesVeryActive_time_series,
                      RR_summary,IRN_notifications,
                      HR_time_series,HRV_summary,
                      ECG_log_list,ECG_recordings,
                      Sleep_goal,Sleep_log,Sleep_log_list,
                      SpO2_summary,
                      RR_intraday,HRV_intraday,SpO2_intraday,HR_intraday_1s,
                      HR_intraday_total,Daily_activity_summary_total,
                      Calories_intraday_total,Distance_intraday_total,Elevation_intraday_total,Floors_intraday_total,Steps_intraday_total], dtype=object)

##Write files out as separate json files
# Build name->value mapping for writing
name_value = dict(zip(filenames, filelist))

# Define non-cardiac names to skip when --cardiac-only
non_cardiac = set([
    "AZM_summary","Activity_goals_daily","Activity_goals_weekly","Activity_log_list","Activity_types","Lifetime_stats",
    "Calories_time_series","Distance_time_series","Elevation_time_series","Floors_time_series","Steps_time_series",
    "activityCalories_time_series","caloriesBMR_time_series","minutesSedentary_time_series","minutesLightlyActive_time_series","minutesFairlyActive_time_series","minutesVeryActive_time_series",
    "Daily_activity_summary",
    "Calories_intraday","Distance_intraday","Elevation_intraday","Floors_intraday","Steps_intraday"
])
# IRN and denser HR are cardiac; keep them even in cardiac-only mode

for name, value in name_value.items():
    if args.cardiac_only and name in non_cardiac:
        continue
    if value in ({}, []) or (isinstance(value, list) and len(value) == 0):
        continue
    jsonpath = base / (f"{name}.json")
    jsonpath.write_text(json.dumps(value, ensure_ascii=False, indent=4))

# Archive JSON outputs for provenance
try:
    zip_path = base / 'exports_provenance.zip'
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for p in base.glob('*.json'):
            zf.write(p, arcname=p.name)
    if args.verbose:
        print(f"Archived JSON outputs to {zip_path}")
except Exception as _e:
    if args.verbose:
        print('Failed to create provenance archive:', _e)


