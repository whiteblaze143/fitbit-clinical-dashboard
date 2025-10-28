import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path
import subprocess


def read_participants(registry_path: Path):
    if not registry_path.exists():
        return []
    rows = []
    with registry_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def parse_date(s: str):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Batch export Fitbit data for all active participants")
    parser.add_argument("--days", type=int, default=7, help="Number of days to export ending today (default 7)")
    parser.add_argument("--cardiac-only", action="store_true", help="Fetch only cardiac endpoints")
    parser.add_argument("--verbose", action="store_true", help="Verbose exporter output")
    parser.add_argument("--participants", default="fitbit/participants.csv", help="Path to participants registry CSV")
    args = parser.parse_args()

    today = datetime.utcnow().date()
    start_default = today - timedelta(days=args.days)

    registry = Path(args.participants)
    participants = read_participants(registry)
    processed = 0
    failures = []

    for p in participants:
        status = (p.get("status") or "").lower().strip()
        if status not in {"enrolled", "paused"}:  # skip invited/withdrawn/completed
            continue
        study_id = (p.get("studyId") or "").strip()
        if not study_id:
            continue
        # Compute date range
        start_date = parse_date((p.get("startDate") or "").strip()) or start_default
        end_date = today
        if start_date > end_date:
            start_date = end_date

        cmd = [
            sys.executable,
            str(Path("fitbit") / "run_export_ecg.py"),
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            str(Path("fitbit_exports") / study_id),
            study_id,
        ]
        if args.cardiac_only:
            cmd.append("--cardiac-only")
        if args.verbose:
            cmd.append("--verbose")
        # derive token file via --participant
        cmd.extend(["--participant", study_id])

        print("Running:", " ".join(cmd))
        try:
            res = subprocess.run(cmd, text=True)
            if res.returncode != 0:
                failures.append(study_id)
            else:
                processed += 1
        except Exception:
            failures.append(study_id)

    # Write summary
    logs_dir = Path("logs") / "fitbit"
    logs_dir.mkdir(parents=True, exist_ok=True)
    summary_path = logs_dir / f"batch_summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        import json
        summary = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "processed": processed,
            "failures": failures,
            "participants": len(participants),
        }
        summary_path.write_text(json.dumps(summary, indent=2))
        print(f"Wrote {summary_path}")
    except Exception:
        pass


if __name__ == "__main__":
    main()


