# Fitbit exporter and viewer

This subfolder contains the Fitbit OAuth helpers and ECG exporter used by the project, plus notes on data artifacts and a quick viewer.

## OAuth setup (Authorization Code)

Fitbit often blocks the implicit flow (unauthorized_client). Use Authorization Code flow.

1) Configure your app at https://dev.fitbit.com/apps
   - OAuth 2.0 Application Type: Server
   - Redirect URL: http://localhost:8080/callback (keep consistent with your environment)
   - Scopes (minimum): electrocardiogram, profile, settings, heartrate

2) Provide credentials via environment OR `.env` at repo root.

PowerShell environment variables:
```powershell
$env:FITBIT_CLIENT_ID = "<your_client_id>"
$env:FITBIT_CLIENT_SECRET = "<your_client_secret>"
$env:FITBIT_REDIRECT_URI = "http://localhost:8080/callback"
$env:FITBIT_SCOPES = "electrocardiogram heartrate profile settings"
```

Or create `.env`:
```
FITBIT_CLIENT_ID=<your_client_id>
FITBIT_CLIENT_SECRET=<your_client_secret>
FITBIT_REDIRECT_URI=http://localhost:8080/callback
FITBIT_SCOPES=electrocardiogram heartrate profile settings
```

3) Authorize and persist tokens:
```powershell
python fitbit/get_fitbit_token.py
```
This opens a browser window and stores tokens in `fitbit/token_store.json` (overridable with `FITBIT_TOKEN_FILE`).

Safe debug (no secrets printed):
```powershell
$env:FITBIT_DEBUG_CONFIG = "1"
```

## Export ECG data

Preferred wrapper (auto-refresh, flags, safe logging):
```powershell
python fitbit/run_export_ecg.py <START_DATE> <END_DATE> <OUTPUT_DIR> [USER_ID] [--cardiac-only] [--verbose]
```
If USER_ID is omitted, the `user_id` in the token store is used.

Direct exporter (advanced):
```powershell
python fitbit/WebAPI_export.py <USER_ID> <START> <END> <OUT_DIR> <ACCESS_TOKEN> [--cardiac-only] [--verbose]
```

Notes:
- ECG list respects Fitbit limits (limit<=10) and follows `pagination.next` until empty.
- Only writes under the specified output directory.

## Artifacts and schemas

- `ECG_summary.csv`: per-recording metadata (startTime, classification, averageHeartRate, samplingFrequency, scalingFactor, device/firmware, stableEcgId, …)
- `ECG_waveforms_index.csv`: lookup for waveform files with `stableEcgId`, `csvPath`, `samplingFrequency`, `durationSeconds`, `scalingFactor`, `classification`, `leadNumber`.
- `ecg_waveforms/<stableEcgId>.csv`: columns `timeSec`, `value` (raw), and `mV` (scaled using `scalingFactor`, default 10922 if absent).
- `daily_cardiac_summary.csv`: compact HR/HRV/SpO2/RR per day (where available).

## Viewer (Streamlit)

Run:
```powershell
streamlit run apps/streamlit_app.py
```

Features:
- Waveform selection by `stableEcgId` with date/class filters
- Amplitude unit toggle: mV, µV, or raw
- Optional lead filter when `leadNumber` exists
- Start offset slider, 5–15 Hz QRS bandpass, R-peak overlay
- HR, RMSSD, SDNN, pNN50 window metrics + RR tachogram
- Mark artifact per recording and CSV download of the displayed segment

## Utilities and validation

```powershell
python scripts/print_token_scopes.py           # Safe token scope print
python scripts/coverage_report.py fitbit_exports
python scripts/validate_ecg_exports.py fitbit_exports
```

## Troubleshooting

- unauthorized_client during consent: ensure Application Type=Server and Redirect URI matches exactly (e.g., http://localhost:8080/callback)
- Empty ECG exports: confirm `electrocardiogram` scope and that recordings exist in the requested window
- 403 on intraday HR/HRV/RR/SpO2: intraday often requires partner access





