from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from backend.db.database import Base

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    stableEcgId = Column(String, unique=True, index=True)
    artifact = Column(Boolean, default=False)

class WindowMetric(Base):
    __tablename__ = "window_metrics"

    id = Column(Integer, primary_key=True, index=True)
    stableEcgId = Column(String, index=True)
    startTime = Column(String)
    classification = Column(String)
    fs = Column(Float)
    window_sec = Column(Float)
    start_at_sec = Column(Float)
    unit = Column(String)
    hr_bpm = Column(Float, nullable=True)
    rmssd_ms = Column(Float, nullable=True)
    sdnn_ms = Column(Float, nullable=True)
    pnn50_pct = Column(Float, nullable=True)
    artifact = Column(Boolean, default=False)

class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True)
    stableEcgId = Column(String, index=True)
    startTime = Column(String)
    classification = Column(String)
    label = Column(String)
    comment = Column(Text, nullable=True)

class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(String, index=True)
    wear_days = Column(Integer)
    daily_ecg_freq = Column(String)
    ease_use = Column(Integer)
    tech_issues = Column(String) # Semicolon separated
    skin_tone = Column(String)
    comments = Column(Text, nullable=True)
