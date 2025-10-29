import argparse
import subprocess
import sys
from pathlib import Path

from token_manager import ensure_access_token, ensure_access_token_from, TokenError


def main():
    parser = argparse.ArgumentParser(description="Run exporter with fresh Fitbit token")
    parser.add_argument("startDate", help="YYYY-MM-DD")
    parser.add_argument("endDate", help="YYYY-MM-DD")
    parser.add_argument("output", help="Output folder for JSON exports")
    parser.add_argument("user", nargs="?", default=None, help="Fitbit user ID (optional; will use token user_id if omitted)")
    parser.add_argument("--cardiac-only", action="store_true", help="Fetch only cardiac endpoints")
    parser.add_argument("--verbose", action="store_true", help="Verbose exporter output")
    parser.add_argument("--clean-output", action="store_true", help="Remove old tiny artifacts and waveform files in output before export")
    parser.add_argument("--no-delete-empties", action="store_true", help="Do not delete tiny/empty export files after run (default is to delete)")
    parser.add_argument("--participant", help="studyId for deriving token and output folder if not provided")
    parser.add_argument("--token-file", help="Explicit token file path (overrides participant)")
    args = parser.parse_args()

    # Resolve token and user id (supports per-participant token files)
    try:
        if args.token_file:
            access_token, user_id = ensure_access_token_from(Path(args.token_file))
        elif args.participant:
            access_token, user_id = ensure_access_token_from(Path("fitbit") / "tokens" / f"{args.participant}.json")
        else:
            access_token, user_id = ensure_access_token()
        if not access_token or not user_id:
            print("Token file incomplete. Re-authorize to obtain access_token and user_id.")
            sys.exit(1)
    except TokenError as e:
        print(f"Token error: {e}")
        sys.exit(1)

    user = args.user or user_id
    # Derive output folder if omitted and participant provided
    output = Path(args.output)
    if str(output).strip() in {".", "", "-"} and args.participant:
        output = Path("fitbit_exports") / args.participant

    # Optionally clean output directory of tiny placeholder artifacts and waveform directory
    if args.clean_output:
        removed = 0
        if output.exists():
            for p in output.iterdir():
                try:
                    if p.is_file():
                        # Remove very small files (<= 4 bytes) and prior indexes for clarity
                        if p.stat().st_size <= 4 or p.name in {"ECG_waveforms_index.csv"}:
                            p.unlink()
                            removed += 1
                    elif p.is_dir() and p.name == "ecg_waveforms":
                        for wf in p.glob("**/*"):
                            try:
                                wf.unlink()
                            except Exception:
                                pass
                        try:
                            p.rmdir()
                        except Exception:
                            pass
                except Exception:
                    pass
        if args.verbose:
            print(f"Cleaned {removed} small files and cleared waveform folder in {output}.")

    # Build command to call exporter
    cmd = [
        sys.executable,
        str(Path(__file__).parent / "WebAPI_export.py"),
        user,
        args.startDate,
        args.endDate,
        str(output),
        access_token,
    ]
    if args.cardiac_only:
        cmd.append("--cardiac-only")
    if args.verbose:
        cmd.append("--verbose")
    # Pass through verbosity; clean-output handled locally
    # Mask token in printed command for safety
    safe_cmd = cmd.copy()
    if len(safe_cmd) >= 6:
        safe_cmd[5] = "<ACCESS_TOKEN>"
    print("Running:", " ".join(safe_cmd))
    result = subprocess.run(cmd, text=True)

    # Default post-run cleanup: remove tiny/empty files to avoid confusion
    # Skips waveform CSVs unless they are zero-byte
    if not args.no_delete_empties:
        removed_after = 0
        if output.exists():
            for p in output.rglob("*"):
                try:
                    if p.is_file():
                        size = p.stat().st_size
                        # Remove very small JSON/CSV placeholders (<= 4 bytes)
                        if size <= 4:
                            # Keep waveform CSVs unless zero-byte
                            if p.parent.name == "ecg_waveforms" and size > 0:
                                continue
                            p.unlink()
                            removed_after += 1
                except Exception:
                    pass
        if args.verbose:
            print(f"Post-run cleanup removed {removed_after} tiny file(s) in {output}.")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
