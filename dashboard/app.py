import os
import json
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go

# Optional scientific tools (guarded aliases to satisfy type checkers)
try:
    from scipy.signal import find_peaks as sp_find_peaks, butter as sp_butter, filtfilt as sp_filtfilt
    _HAS_SCIPY = True
except Exception:
    sp_find_peaks = None  # type: ignore[assignment]
    sp_butter = None      # type: ignore[assignment]
    sp_filtfilt = None    # type: ignore[assignment]
    _HAS_SCIPY = False

# Allow overriding exports directory via environment variable
BASE = Path(os.getenv('FITBIT_EXPORTS_DIR', str(Path(__file__).resolve().parents[1] / 'fitbit_exports')))
SUMMARY_CSV = BASE / 'ECG_summary.csv'
INDEX_CSV = BASE / 'ECG_waveforms_index.csv'
WAVE_DIR = BASE / 'ecg_waveforms'
DAILY_CSV = BASE / 'daily_cardiac_summary.csv'
AF_SCORES_CSV = BASE / 'af_scores.csv'

# App-local persisted artifacts/metrics files
APP_DATA_DIR = Path(__file__).resolve().parents[1] / 'apps' / 'app_data'
ARTIFACT_CSV = APP_DATA_DIR / 'ecg_artifacts.csv'
METRICS_CSV = APP_DATA_DIR / 'ecg_window_metrics.csv'
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Labels CSV lives alongside app-local data
LABELS_CSV = APP_DATA_DIR / 'ecg_labels.csv'

def load_data():
    summary = pd.read_csv(SUMMARY_CSV) if SUMMARY_CSV.exists() else pd.DataFrame()
    index = pd.read_csv(INDEX_CSV) if INDEX_CSV.exists() else pd.DataFrame()
    daily = pd.read_csv(DAILY_CSV) if DAILY_CSV.exists() else pd.DataFrame()
    af_scores = pd.read_csv(AF_SCORES_CSV) if AF_SCORES_CSV.exists() else pd.DataFrame()
    return summary, index, daily, af_scores

st.set_page_config(
    page_title='Fitbit Clinical Dashboard', 
    layout='wide',
    initial_sidebar_state='auto',
    page_icon='🏥'
)

# Enhanced CSS styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏥 Fitbit Clinical Dashboard</h1>
    <p style="margin: 0; opacity: 0.9;">Pilot Feasibility Study • AFib Monitoring</p>
</div>
""", unsafe_allow_html=True)

# Load available participants first
FITBIT_ROOT = Path(__file__).resolve().parents[1] / 'fitbit_exports'
available_participants = [d.name for d in FITBIT_ROOT.iterdir() if d.is_dir()]
if not available_participants:
    available_participants = ['default']

# Quick Actions Bar
st.markdown("### 🚀 Quick Actions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 Refresh Data", help="Reload all participant data", use_container_width=True):
        st.rerun()

with col2:
    if st.button("📥 Batch Export", help="Export data for all participants", use_container_width=True):
        st.code("python scripts/batch_export_all.py --days 7 --cardiac-only --verbose")
        st.info("Run this command in terminal to export data for all participants")

with col3:
    if st.button("👥 View Compliance", help="See all participant compliance metrics", use_container_width=True):
        st.info("Switch to Compliance tab to see adherence metrics")

with col4:
    if st.button("🔐 Authorize Participant", help="Setup new participant authentication", use_container_width=True):
        st.code("python fitbit/get_fitbit_token.py --participant <STUDY_ID>")
        st.info("⚠️ Run on secure Sunnybrook machine only!")

st.markdown("---")

# Study protocol highlights and contacts (per supervisor email chain)
with st.expander("Study protocol and contacts"):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("""
        **Short Title**: FitBit ECG Study  
        **Protocol**: Evaluation of Fitbit Monitoring to Detect Recurrent AF  
        **Version**: 1.1  
        **Date**: October 21, 2025

        - Single-centre pilot feasibility cohort at Sunnybrook Health Sciences Centre
        - Two arms: post-ablation and post-cardioversion (initial target: 10 + 10)
        - Daily smartwatch ECG for up to 6 months or until AF recurrence
        - Intermittent clinical monitoring at ~3 and ~6 months (e.g., external patch monitor)
        - All data stored locally on a Sunnybrook password-protected workstation
        """)
    with col_b:
        st.markdown("""
        **Primary Contact**  
        Dr. Christopher Cheung  
        Email: christopher.cheung@sunnybrook.ca  
        Phone: 416-480-4746

        **Secondary Contact**  
        Mithun Manivannan  
        Email: mithun.manivannan@sri.utoronto.ca
        """)

    st.info("DRAFT PROTOCOL - DO NOT DISTRIBUTE")

#

# Study Overview Metrics
st.markdown("### 📊 Study Overview")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_participants = len(available_participants)
    st.metric("Total Participants", total_participants, help="Current enrolled participants")

with col2:
    # Count ablation arm (assuming studyId pattern like ABL01, ABL02...)
    ablation_count = len([p for p in available_participants if 'ABL' in p.upper() or 'A' == p[0].upper()])
    st.metric("Ablation Arm (pilot)", f"{ablation_count}/10", help="Pilot target: 10 participants")

with col3:
    # Count cardioversion arm (assuming studyId pattern like CVR01, CVR02...)
    cardioversion_count = len([p for p in available_participants if 'CVR' in p.upper() or 'C' == p[0].upper()])
    st.metric("Cardioversion Arm (pilot)", f"{cardioversion_count}/10", help="Pilot target: 10 participants")

with col4:
    # Check for recent data (within last 2 days)
    active_count = 0
    for pid in available_participants:
        summary_path = FITBIT_ROOT / pid / 'ECG_summary.csv'
        if summary_path.exists():
            try:
                df = pd.read_csv(summary_path)
                if not df.empty and 'startTime' in df.columns:
                    last_ecg = pd.to_datetime(df['startTime'].iloc[-1])
                    if (pd.Timestamp.now() - last_ecg).days <= 2:
                        active_count += 1
            except:
                pass
    st.metric("Active (48h)", active_count, help="Participants with ECG in last 48 hours")

with col5:
    # Calculate overall compliance
    if total_participants > 0:
        compliance_rate = (active_count / total_participants * 100) if total_participants > 0 else 0
        st.metric("Overall Adherence", f"{compliance_rate:.0f}%", 
                 delta=f"{compliance_rate - 70:.0f}%" if compliance_rate >= 70 else f"{compliance_rate - 70:.0f}%",
                 help="Target: 70% daily adherence")

st.markdown("---")

summary, index, daily, af_scores = load_data()

if summary.empty:
    st.warning('ECG_summary.csv not found or empty. Run the exporter first.')
else:
    st.subheader('ECG Summary')
    st.dataframe(summary)
    # Classification counts
    try:
        if 'classification' in summary.columns:
            counts = summary['classification'].value_counts().reset_index()
            counts.columns = ['classification', 'count']
            st.bar_chart(counts.set_index('classification'))
    except Exception:
        pass

if index.empty:
    st.info('ECG_waveforms_index.csv not found. If your API payload lacks waveformSamples, rerun on dates that include waveforms.')
else:
    st.subheader('Waveform Viewer')
    # Sidebar filters and controls
    with st.sidebar:
        st.header('Filters')
        date_options = sorted({str(x)[:10] for x in index['startTime']}) if 'startTime' in index.columns else []
        selected_date = st.selectbox('Date', date_options, index=len(date_options)-1 if date_options else 0)
        class_options = sorted(idx for idx in index.get('classification', pd.Series(['NA'])).dropna().unique()) if 'classification' in index.columns else []
        selected_classes = st.multiselect('Classification', class_options, default=class_options)
        window_sec = st.slider('Window length (s)', min_value=5, max_value=20, value=10, step=1)
        # Optional lead filter if available
        lead_options = []
        selected_lead = None
        if 'leadNumber' in index.columns:
            try:
                lead_options = sorted([int(x) for x in pd.to_numeric(index['leadNumber'], errors='coerce').dropna().unique()])
            except Exception:
                lead_options = sorted([str(x) for x in index['leadNumber'].dropna().unique()])
            if lead_options:
                selected_lead = st.selectbox('Lead', options=["All"] + list(lead_options), index=0)

    df_index = index
    if 'startTime' in index.columns and selected_date:
        df_index = df_index[df_index['startTime'].astype(str).str.startswith(selected_date)]
    if 'classification' in df_index.columns and selected_classes:
        df_index = df_index[df_index['classification'].isin(selected_classes)]
    # Apply optional lead filter
    if selected_lead is not None and selected_lead != "All" and 'leadNumber' in df_index.columns:
        if isinstance(selected_lead, int):
            df_index = df_index[pd.to_numeric(df_index['leadNumber'], errors='coerce') == selected_lead]
        else:
            df_index = df_index[df_index['leadNumber'].astype(str) == str(selected_lead)]

    sid_options = df_index['stableEcgId'].astype(str).tolist() if 'stableEcgId' in df_index.columns else []
    selected_sid = st.selectbox('Select stableEcgId', sid_options)

    def _bandpass_mv(sig, fs):
        if not _HAS_SCIPY or sp_butter is None or sp_filtfilt is None:
            return sig
        try:
            # 5-15 Hz band for QRS enhancement
            nyq = 0.5 * fs
            assert sp_butter is not None and sp_filtfilt is not None
            b, a = sp_butter(2, [5/nyq, 15/nyq], btype='band')  # type: ignore
            return sp_filtfilt(b, a, sig)  # type: ignore
        except Exception:
            return sig

    def _rr_metrics(peaks, fs):
        if len(peaks) < 3:
            return np.nan, np.nan, np.nan, np.nan
        rr = np.diff(peaks) / fs
        if len(rr) < 2:
            hr_only = float(60.0/rr.mean()) if rr.mean() > 0 else np.nan
            return hr_only, np.nan, np.nan, np.nan
        hr = float(60.0 / np.mean(rr)) if np.mean(rr) > 0 else np.nan
        sdnn = float(np.std(rr, ddof=1) * 1000.0)
        diff_rr = np.diff(rr)
        rmssd = float(np.sqrt(np.mean(diff_rr**2)) * 1000.0)
        pnn50 = float(np.mean(np.abs(diff_rr) > 0.05) * 100.0)
        return hr, rmssd, sdnn, pnn50

    if selected_sid:
        row = df_index[df_index['stableEcgId'].astype(str) == selected_sid].iloc[0]
        fs = float(row.get('samplingFrequency', 250.0))
        rel = row.get('csvPath', f'ecg_waveforms/{selected_sid}.csv')
        path = (BASE / rel) if isinstance(rel, str) else (WAVE_DIR / f'{selected_sid}.csv')
        # Preferred unit defaults to mV if scalingFactor exists and >0
        preferred_unit = 'mV' if float(row.get('scalingFactor', 0) or 0) > 0 else 'raw integer'
        with st.sidebar:
            unit_choice = st.radio('Amplitude unit', options=['mV', 'µV', 'raw integer'], index=(0 if preferred_unit == 'mV' else 2))
            smooth = st.checkbox('Bandpass filter (5–15 Hz)', value=_HAS_SCIPY)
            # Artifact toggle (persisted)
            artifact_default = False
            try:
                if ARTIFACT_CSV.exists():
                    a = pd.read_csv(ARTIFACT_CSV)
                    if not a.empty and 'stableEcgId' in a and 'artifact' in a:
                        match = a[a['stableEcgId'].astype(str) == selected_sid]
                        if not match.empty:
                            artifact_default = bool(match.iloc[0]['artifact'])
            except Exception:
                pass
            artifact = st.checkbox('Mark as artifact', value=artifact_default)
        if path.exists():
            df = pd.read_csv(path)
            # Normalize columns
            if 'timeSec' in df.columns:
                t = df['timeSec'].to_numpy()
                # amplitude selection
                if unit_choice in ('mV', 'µV') and 'mV' in df.columns:
                    v = df['mV'].to_numpy()
                    if unit_choice == 'µV':
                        v = v * 1000.0
                elif 'value' in df.columns:
                    v = df['value'].to_numpy()
                else:
                    num_df = df.select_dtypes(include=[np.number])
                    v = num_df.iloc[:, 1].to_numpy() if num_df.shape[1] >= 2 else df[df.columns[1]].to_numpy()
                # Fs sanity from time deltas
                if len(t) > 2:
                    dt = np.median(np.diff(t))
                    if dt > 0:
                        fs_est = 1.0 / dt
                        if abs(fs_est - fs) / fs > 0.02:
                            st.warning(f"Sampling frequency mismatch: index={fs:.1f} Hz, estimated~{fs_est:.1f} Hz")
            else:
                if unit_choice == 'mV' and 'mV' in df.columns:
                    v = df['mV'].to_numpy()
                elif unit_choice == 'µV' and 'mV' in df.columns:
                    v = (df['mV'].to_numpy()) * 1000.0
                elif 'value' in df.columns:
                    v = df['value'].to_numpy()
                else:
                    v = df.select_dtypes(include=[np.number]).iloc[:, 0].to_numpy()
                t = np.arange(len(v)) / fs

            # Show metadata above the plot
            meta = {
                'Start': str(row.get('startTime', 'NA')),
                'Classification': str(row.get('classification', 'NA')),
                'Fs (Hz)': f"{fs:.1f}",
            }
            try:
                if not summary.empty and 'stableEcgId' in summary.columns:
                    sm = summary[summary['stableEcgId'].astype(str) == selected_sid]
                    if not sm.empty:
                        dev_name = sm.iloc[0].get('deviceName')
                        fw = sm.iloc[0].get('firmwareVersion')
                        avg_hr = sm.iloc[0].get('averageHeartRate')
                        if dev_name or fw:
                            meta['Device'] = f"{dev_name or 'NA'} ({fw or 'fw?'})"
                        if isinstance(avg_hr, (int, float)) and avg_hr == avg_hr:
                            meta['Avg HR (bpm)'] = f"{float(avg_hr):.1f}"
            except Exception:
                pass
            # AF score if available
            af_txt = None
            try:
                if not af_scores.empty and 'stableEcgId' in af_scores.columns:
                    a = af_scores[af_scores['stableEcgId'].astype(str) == selected_sid]
                    if not a.empty:
                        if 'af_proba' in a.columns and a['af_proba'].notna().any():
                            af_txt = f"AF probability: {float(a.iloc[0]['af_proba']):.2f}"
                        elif 'anomaly_score' in a.columns and a['anomaly_score'].notna().any():
                            af_txt = f"AF anomaly score: {float(a.iloc[0]['anomaly_score']):.2f}"
            except Exception:
                pass

            if af_txt:
                st.caption(' • '.join([f"{k}: {v}" for k, v in meta.items()]) + f" • {af_txt}")
            else:
                st.caption(' • '.join([f"{k}: {v}" for k, v in meta.items()]))

            # Window controls: start offset based on available duration
            total_sec = float(len(v) / fs)
            with st.sidebar:
                start_at = st.slider('Start at (s)', min_value=0.0, max_value=max(0.0, float(max(total_sec - window_sec, 0))), value=0.0, step=0.5)
            s0 = int(start_at * fs)
            s1 = int(min(len(v), s0 + int(window_sec * fs)))

            # Optional bandpass smoothing
            v_disp = v.copy()
            if smooth and _HAS_SCIPY and unit_choice == 'mV':
                v_disp = _bandpass_mv(v_disp - np.median(v_disp), fs)

            if unit_choice == 'mV' and ('mV' in df.columns):
                y_label = 'Amplitude (mV)'
            elif unit_choice == 'µV' and ('mV' in df.columns):
                y_label = 'Amplitude (µV)'
            else:
                y_label = 'Amplitude (raw)'

            # Peak detection on displayed window
            peaks = np.array([])
            if (s1 - s0) > int(2 * fs):
                v_seg = v_disp[s0:s1]
                if _HAS_SCIPY and sp_find_peaks is not None:
                    distance = int(0.25 * fs)
                    prominence = max(0.1, float(np.std(v_seg) * 0.5))
                    assert sp_find_peaks is not None
                    peaks, _ = sp_find_peaks(v_seg, distance=distance, prominence=prominence)  # type: ignore
                else:
                    thr = np.percentile(np.abs(v_seg), 85)
                    cand = np.where((v_seg[1:-1] > thr) & (v_seg[1:-1] > v_seg[:-2]) & (v_seg[1:-1] > v_seg[2:]))[0] + 1
                    refractory = int(0.25 * fs)
                    sel, last = [], -refractory
                    for p in cand:
                        if p - last >= refractory:
                            sel.append(p); last = p
                    peaks = np.array(sel)

            # Build Plotly figure with optional peak overlay
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t[s0:s1], y=v_disp[s0:s1], mode='lines', name='ECG'))
            if peaks.size > 0:
                fig.add_trace(go.Scatter(x=t[s0:s1][peaks], y=v_disp[s0:s1][peaks], mode='markers', name='R-peaks', marker=dict(color='red', size=6)))
            fig.update_layout(height=300, margin=dict(l=40, r=20, t=30, b=40), yaxis_title=y_label, xaxis_title='Time (s)')
            st.plotly_chart(fig, use_container_width=True)

            # Peak detection and metrics
            hr = rmssd = sdnn = pnn50 = float('nan')
            if (s1 - s0) > int(2 * fs):
                if peaks.size >= 3:
                    # Peaks were computed on v_disp; use them to compute RR metrics
                    hr, rmssd, sdnn, pnn50 = _rr_metrics(peaks, fs)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric('HR (bpm)', f"{hr:.1f}" if hr == hr else 'NA')
            col2.metric('RMSSD (ms)', f"{rmssd:.1f}" if rmssd == rmssd else 'NA')
            col3.metric('SDNN (ms)', f"{sdnn:.1f}" if sdnn == sdnn else 'NA')
            col4.metric('pNN50 (%)', f"{pnn50:.1f}" if pnn50 == pnn50 else 'NA')

            # RR tachogram
            if peaks.size >= 3:
                rr = np.diff(peaks) / fs
                rr_t = t[s0:s1][peaks[1:]]
                st.line_chart(pd.DataFrame({'time_s': rr_t, 'RR (s)': rr}).set_index('time_s'))

            # Persist artifact flag
            try:
                a = pd.DataFrame([{'stableEcgId': selected_sid, 'artifact': bool(artifact)}])
                if ARTIFACT_CSV.exists():
                    old = pd.read_csv(ARTIFACT_CSV)
                    old = old[old['stableEcgId'].astype(str) != selected_sid]
                    a = pd.concat([old, a], ignore_index=True)
                a.to_csv(ARTIFACT_CSV, index=False)
            except Exception:
                st.warning('Could not save artifact flag.')

            # Save metrics button and download displayed segment
            if st.button('Save window metrics to CSV'):
                try:
                    rec = {
                        'stableEcgId': selected_sid,
                        'startTime': row.get('startTime'),
                        'classification': row.get('classification'),
                        'fs': fs,
                        'window_sec': window_sec,
                        'start_at_sec': start_at,
                        'unit': unit_choice,
                        'hr_bpm': hr,
                        'rmssd_ms': rmssd,
                        'sdnn_ms': sdnn,
                        'pnn50_pct': pnn50,
                        'artifact': bool(artifact),
                    }
                    m = pd.DataFrame([rec])
                    if METRICS_CSV.exists():
                        om = pd.read_csv(METRICS_CSV)
                        m = pd.concat([om, m], ignore_index=True)
                    m.to_csv(METRICS_CSV, index=False)
                    st.success(f"Saved metrics to {METRICS_CSV}")
                except Exception:
                    st.error('Failed to save metrics.')

            # Labeling UI: NSR / AF / Other / Unsure with comment box
            with st.expander('Label this ECG'):
                # Load existing label if present
                existing = None
                if LABELS_CSV.exists():
                    try:
                        labdf = pd.read_csv(LABELS_CSV)
                        hit = labdf[labdf['stableEcgId'].astype(str) == selected_sid]
                        if not hit.empty:
                            existing = hit.iloc[0].to_dict()
                    except Exception:
                        existing = None
                label_options = ['NSR', 'AF', 'Other', 'Unsure']
                default_idx = 0
                if existing and str(existing.get('label')) in label_options:
                    default_idx = label_options.index(str(existing.get('label')))
                label_choice = st.radio('Label', label_options, index=default_idx, horizontal=True)
                comment_default = existing.get('comment') if existing else ''
                comment = st.text_input('Comment (optional)', value=str(comment_default) if comment_default is not None else '')
                if st.button('Save label'):
                    try:
                        rec = {
                            'stableEcgId': selected_sid,
                            'startTime': row.get('startTime'),
                            'classification': row.get('classification'),
                            'label': label_choice,
                            'comment': comment,
                        }
                        if LABELS_CSV.exists():
                            df_lab = pd.read_csv(LABELS_CSV)
                            df_lab = df_lab[df_lab['stableEcgId'].astype(str) != selected_sid]
                            df_lab = pd.concat([df_lab, pd.DataFrame([rec])], ignore_index=True)
                        else:
                            df_lab = pd.DataFrame([rec])
                        df_lab.to_csv(LABELS_CSV, index=False)
                        st.success('Label saved')
                    except Exception:
                        st.error('Failed to save label')

            # Offer CSV download of the displayed segment
            try:
                seg = pd.DataFrame({
                    'time_s': t[s0:s1],
                    'amplitude': v_disp[s0:s1]
                })
                st.download_button(
                    label='Download displayed segment (CSV)',
                    data=seg.to_csv(index=False).encode('utf-8'),
                    file_name=f"{selected_sid}_segment_{int(start_at)}s_{int(window_sec)}s.csv",
                    mime='text/csv'
                )
                # Full recording download
                full = pd.DataFrame({'time_s': t, 'amplitude': v_disp})
                st.download_button(
                    label='Download full recording (CSV)',
                    data=full.to_csv(index=False).encode('utf-8'),
                    file_name=f"{selected_sid}_full.csv",
                    mime='text/csv'
                )
            except Exception:
                pass
        else:
            st.warning(f'Waveform file not found: {path}')

# Daily trends from daily_cardiac_summary.csv
if not daily.empty:
    st.subheader('Daily cardiac summary')
    if 'date' in daily.columns:
        latest = sorted(daily['date'].dropna().astype(str).unique())[-1]
        day = daily[daily['date'].astype(str) == latest]

        def parse_value(x):
            if isinstance(x, str) and x and x[0] in '{[':
                try:
                    return json.loads(x)
                except Exception:
                    return x
            return x

        day = day.copy()
        day['value_parsed'] = day['value'].apply(parse_value)

        def pick_float(obj, keys=(
            'restingHeartRate','dailyRmssd','deepRmssd','breathingRate','avg','value'
        )):
            if isinstance(obj, (int, float)):
                return float(obj)
            if isinstance(obj, dict):
                for k in keys:
                    if k in obj and isinstance(obj[k], (int, float)):
                        return float(obj[k])
                for v in obj.values():
                    if isinstance(v, (int, float)):
                        return float(v)
            return float('nan')

        metrics = {
            'HR_summary': 'Resting HR (bpm)',
            'HRV': 'Daily RMSSD (ms)',
            'RR': 'Breathing rate (rpm)',
            'SpO2': 'SpO2 avg (%)',
        }
        cols = st.columns(len(metrics))
        for i, (mkey, label) in enumerate(metrics.items()):
            sub = day[day['metric'] == mkey]
            val = float('nan')
            if not sub.empty:
                parsed = sub.iloc[0]['value_parsed']
                val = pick_float(parsed)
            cols[i].metric(label, f"{val:.1f}" if val == val else 'NA')

        # RMSSD trend line
        try:
            d2 = daily.copy()
            d2['value_parsed'] = d2['value'].apply(parse_value)
            d2['date'] = pd.to_datetime(d2['date'])
            hrv = d2[d2['metric'] == 'HRV'].copy()
            if not hrv.empty:
                hrv['rmssd'] = hrv['value_parsed'].apply(pick_float)
                hrv = hrv.dropna(subset=['rmssd']).sort_values('date').tail(60)
                if len(hrv) >= 2:
                    st.line_chart(hrv.set_index('date')['rmssd'])
        except Exception:
            pass

# Acceptability and usability survey (pilot feasibility)
SURVEY_CSV = APP_DATA_DIR / 'acceptability_survey.csv'
with st.expander('Acceptability & usability survey (optional)'):
    st.markdown("""
    Use this lightweight form to collect pilot feedback after monitoring. Do not include PHI; use study IDs only.
    """)
    col1, col2 = st.columns(2)
    with col1:
        study_id = st.text_input('Study ID (e.g., ABL01/CVR01)', value='')
        wear_days = st.number_input('Estimated wear days over period', min_value=0, max_value=200, value=0, step=1)
        daily_ecg_freq = st.selectbox('Daily ECG adherence', ['<25%', '25-50%', '50-75%', '75-90%', '>90%'])
    with col2:
        ease_use = st.select_slider('Ease of use (1=hard, 5=easy)', options=[1,2,3,4,5], value=4)
        tech_issues = st.multiselect('Any technical issues encountered?', ['Pairing', 'Battery', 'App navigation', 'ECG app use', 'Syncing', 'Other'])
        skin_tone = st.selectbox('Skin tone (Fitzpatrick-like self-report)', ['Prefer not to say','I-II','III-IV','V-VI'])
    comments = st.text_area('Comments (optional)', value='')
    if st.button('Save survey response'):
        if not study_id.strip():
            st.warning('Study ID is required to save a survey response.')
        else:
            try:
                rec = pd.DataFrame([{
                    'study_id': study_id.strip(),
                    'wear_days': int(wear_days),
                    'daily_ecg_freq': daily_ecg_freq,
                    'ease_use': int(ease_use),
                    'tech_issues': ';'.join(tech_issues) if tech_issues else '',
                    'skin_tone': skin_tone,
                    'comments': comments,
                }])
                if SURVEY_CSV.exists():
                    old = pd.read_csv(SURVEY_CSV)
                    # de-duplicate by study_id (keep latest)
                    old = old[old['study_id'].astype(str) != study_id.strip()]
                    rec = pd.concat([old, rec], ignore_index=True)
                rec.to_csv(SURVEY_CSV, index=False)
                st.success('Survey response saved.')
            except Exception as e:
                st.error(f'Failed to save survey: {e}')

    if SURVEY_CSV.exists():
        try:
            s = pd.read_csv(SURVEY_CSV)
            st.dataframe(s)
            st.download_button('Download survey responses (CSV)', data=s.to_csv(index=False).encode('utf-8'), file_name='acceptability_survey.csv', mime='text/csv')
        except Exception:
            st.warning('Could not load existing survey responses.')

# Review tables and downloads
with st.expander('Review & downloads'):
    cols = st.columns(2)
    try:
        if ARTIFACT_CSV.exists():
            a = pd.read_csv(ARTIFACT_CSV)
            cols[0].markdown('**Artifact flags**')
            cols[0].dataframe(a)
            cols[0].download_button('Download artifact flags (CSV)', data=a.to_csv(index=False).encode('utf-8'), file_name='ecg_artifacts.csv', mime='text/csv')
    except Exception:
        pass
    try:
        if METRICS_CSV.exists():
            m = pd.read_csv(METRICS_CSV)
            cols[1].markdown('**Window metrics**')
            cols[1].dataframe(m)
            cols[1].download_button('Download window metrics (CSV)', data=m.to_csv(index=False).encode('utf-8'), file_name='ecg_window_metrics.csv', mime='text/csv')
    except Exception:
        pass
    try:
        if LABELS_CSV.exists():
            labs = pd.read_csv(LABELS_CSV)
            st.markdown('**Labels**')
            st.dataframe(labs)
            st.download_button('Download labels (CSV)', data=labs.to_csv(index=False).encode('utf-8'), file_name='ecg_labels.csv', mime='text/csv')
            # Retrain button (invokes training script via os.system)
            if st.button('Retrain AF model with labels'):
                try:
                    import subprocess, sys
                    cmd = [sys.executable, str(Path(__file__).resolve().parents[1] / 'scripts' / 'train_af_baseline.py')]
                    res = subprocess.run(cmd, capture_output=True, text=True)
                    st.code(res.stdout + '\n' + res.stderr)
                    st.success('Training completed. Reload to refresh AF scores.')
                except Exception as e:
                    st.error(f'Failed to run training: {e}')
    except Exception:
        pass
