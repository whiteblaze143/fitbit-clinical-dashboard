from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from backend.services.participant_service import read_participants, write_participants, get_available_participants_exports
from backend.services.data_service import get_summary_df, get_index_df, get_daily_df, get_waveform_data
from backend.db.database import get_db
from backend.models.models import Artifact, WindowMetric, Label, SurveyResponse

router = APIRouter(prefix="/api")

class ParticipantCreate(BaseModel):
    studyId: str
    firstName: str
    lastName: str
    phone: str
    email: str
    deviceId: str
    status: str
    startDate: str
    endDate: str
    expectedPerDay: str
    notes: str

class ParticipantList(BaseModel):
    participants: List[ParticipantCreate]

@router.get("/participants")
def get_participants():
    return read_participants()

@router.post("/participants")
def update_participants(data: ParticipantList):
    write_participants([p.model_dump() for p in data.participants])
    return {"status": "success"}

@router.get("/study-overview")
def get_study_overview():
    participants = get_available_participants_exports()
    total = len(participants) if participants != ["default"] else 0
    ablation = len([p for p in participants if 'ABL' in p.upper() or p.upper().startswith('A')])
    cardioversion = len([p for p in participants if 'CVR' in p.upper() or p.upper().startswith('C')])

    # Active 48 hours
    active = 0
    import pandas as pd
    for pid in participants:
        df = get_summary_df(pid)
        if not df.empty and 'startTime' in df.columns:
            last_ecg = pd.to_datetime(df['startTime'].iloc[-1])
            if (pd.Timestamp.now() - last_ecg).days <= 2:
                active += 1

    compliance = (active / total * 100) if total > 0 else 0

    return {
        "totalParticipants": total,
        "ablationArm": ablation,
        "cardioversionArm": cardioversion,
        "active48h": active,
        "overallCompliance": round(compliance, 1)
    }

@router.get("/data/summary")
def get_data_summary(participantId: str = None):
    df = get_summary_df(participantId)
    import json
    return json.loads(df.to_json(orient="records"))

@router.get("/data/index")
def get_data_index(participantId: str = None):
    df = get_index_df(participantId)
    # clean NaNs
    df = df.fillna("")
    import json
    return json.loads(df.to_json(orient="records"))

@router.get("/data/daily")
def get_data_daily(participantId: str = None):
    df = get_daily_df(participantId)
    df = df.fillna("")
    import json
    return json.loads(df.to_json(orient="records"))

import numpy as np

# Optional scipy tools
try:
    from scipy.signal import find_peaks, butter, filtfilt
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

def bandpass_filter(sig, fs):
    if not HAS_SCIPY:
        return sig
    try:
        nyq = 0.5 * fs
        b, a = butter(2, [5/nyq, 15/nyq], btype='band')
        return filtfilt(b, a, sig)
    except Exception:
        return sig

@router.get("/data/waveform/{participant_id}/{stable_ecg_id}")
def get_waveform(participant_id: str, stable_ecg_id: str, start_sec: float = 0, window_sec: float = 10, unit: str = 'mV', apply_filter: bool = False, fs: float = 250.0):
    df = get_waveform_data(participant_id, stable_ecg_id, fs)
    if df is None:
        raise HTTPException(status_code=404, detail="Waveform not found")

    # Standardize time and amplitude arrays
    if 'timeSec' in df.columns:
        t = df['timeSec'].to_numpy()
        if unit in ('mV', 'µV') and 'mV' in df.columns:
            v = df['mV'].to_numpy()
            if unit == 'µV':
                v = v * 1000.0
        elif 'value' in df.columns:
            v = df['value'].to_numpy()
        else:
            num_df = df.select_dtypes(include=[np.number])
            v = num_df.iloc[:, 1].to_numpy() if num_df.shape[1] >= 2 else df[df.columns[1]].to_numpy()
    else:
        if unit == 'mV' and 'mV' in df.columns:
            v = df['mV'].to_numpy()
        elif unit == 'µV' and 'mV' in df.columns:
            v = df['mV'].to_numpy() * 1000.0
        elif 'value' in df.columns:
            v = df['value'].to_numpy()
        else:
            v = df.select_dtypes(include=[np.number]).iloc[:, 0].to_numpy()
        t = np.arange(len(v)) / fs

    # Slicing
    total_sec = len(v) / fs
    s0 = int(start_sec * fs)
    s1 = int(min(len(v), s0 + int(window_sec * fs)))

    t_seg = t[s0:s1]
    v_seg = v[s0:s1]

    if apply_filter and unit == 'mV':
        v_seg = bandpass_filter(v_seg - np.median(v_seg), fs)

    # Peak detection
    peaks = []
    hr = None
    rmssd = None
    sdnn = None
    pnn50 = None

    if len(v_seg) > int(2 * fs):
        if HAS_SCIPY:
            distance = int(0.25 * fs)
            prominence = max(0.1, float(np.std(v_seg) * 0.5))
            peak_indices, _ = find_peaks(v_seg, distance=distance, prominence=prominence)
        else:
            thr = np.percentile(np.abs(v_seg), 85)
            cand = np.where((v_seg[1:-1] > thr) & (v_seg[1:-1] > v_seg[:-2]) & (v_seg[1:-1] > v_seg[2:]))[0] + 1
            refractory = int(0.25 * fs)
            sel, last = [], -refractory
            for p in cand:
                if p - last >= refractory:
                    sel.append(int(p))
                    last = p
            peak_indices = np.array(sel)

        peaks = peak_indices.tolist()

        # Metrics
        if len(peak_indices) >= 3:
            rr = np.diff(peak_indices) / fs
            if len(rr) >= 2:
                hr = float(60.0 / np.mean(rr)) if np.mean(rr) > 0 else None
                sdnn = float(np.std(rr, ddof=1) * 1000.0)
                diff_rr = np.diff(rr)
                rmssd = float(np.sqrt(np.mean(diff_rr**2)) * 1000.0)
                pnn50 = float(np.mean(np.abs(diff_rr) > 0.05) * 100.0)

    return {
        "time": t_seg.tolist(),
        "amplitude": v_seg.tolist(),
        "peaks": peaks,
        "metrics": {
            "hr": hr,
            "rmssd": rmssd,
            "sdnn": sdnn,
            "pnn50": pnn50
        },
        "total_sec": total_sec
    }

# App DB Routes
class ArtifactUpdate(BaseModel):
    stableEcgId: str
    artifact: bool

@router.post("/db/artifacts")
def set_artifact(data: ArtifactUpdate, db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.stableEcgId == data.stableEcgId).first()
    if artifact:
        artifact.artifact = data.artifact
    else:
        artifact = Artifact(stableEcgId=data.stableEcgId, artifact=data.artifact)
        db.add(artifact)
    db.commit()
    return {"status": "success"}

@router.get("/db/artifacts/{stable_ecg_id}")
def get_artifact(stable_ecg_id: str, db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.stableEcgId == stable_ecg_id).first()
    return {"artifact": artifact.artifact if artifact else False}


class MetricUpdate(BaseModel):
    stableEcgId: str
    startTime: str
    classification: str
    fs: float
    window_sec: float
    start_at_sec: float
    unit: str
    hr_bpm: Optional[float] = None
    rmssd_ms: Optional[float] = None
    sdnn_ms: Optional[float] = None
    pnn50_pct: Optional[float] = None
    artifact: bool

@router.post("/db/metrics")
def save_metrics(data: MetricUpdate, db: Session = Depends(get_db)):
    metric = WindowMetric(**data.model_dump())
    db.add(metric)
    db.commit()
    return {"status": "success"}


class LabelUpdate(BaseModel):
    stableEcgId: str
    startTime: str
    classification: str
    label: str
    comment: Optional[str] = None

@router.post("/db/labels")
def save_label(data: LabelUpdate, db: Session = Depends(get_db)):
    # overwrite existing
    existing = db.query(Label).filter(Label.stableEcgId == data.stableEcgId).first()
    if existing:
        existing.label = data.label
        existing.comment = data.comment
    else:
        new_label = Label(**data.model_dump())
        db.add(new_label)
    db.commit()
    return {"status": "success"}

@router.get("/db/labels/{stable_ecg_id}")
def get_label(stable_ecg_id: str, db: Session = Depends(get_db)):
    label = db.query(Label).filter(Label.stableEcgId == stable_ecg_id).first()
    return label or {}

class SurveyCreate(BaseModel):
    study_id: str
    wear_days: int
    daily_ecg_freq: str
    ease_use: int
    tech_issues: List[str]
    skin_tone: str
    comments: Optional[str] = None

@router.post("/db/survey")
def submit_survey(data: SurveyCreate, db: Session = Depends(get_db)):
    existing = db.query(SurveyResponse).filter(SurveyResponse.study_id == data.study_id).first()

    issues_str = ";".join(data.tech_issues)

    if existing:
        existing.wear_days = data.wear_days
        existing.daily_ecg_freq = data.daily_ecg_freq
        existing.ease_use = data.ease_use
        existing.tech_issues = issues_str
        existing.skin_tone = data.skin_tone
        existing.comments = data.comments
    else:
        survey = SurveyResponse(
            study_id=data.study_id,
            wear_days=data.wear_days,
            daily_ecg_freq=data.daily_ecg_freq,
            ease_use=data.ease_use,
            tech_issues=issues_str,
            skin_tone=data.skin_tone,
            comments=data.comments
        )
        db.add(survey)

    db.commit()
    return {"status": "success"}
