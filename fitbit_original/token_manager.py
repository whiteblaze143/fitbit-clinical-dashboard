import os
try:
    # Load .env early so os.getenv picks up FITBIT_* by default
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; proceed if not installed
    pass
import json
import time
import base64
import requests
from pathlib import Path

TOKEN_FILE = Path(os.getenv("FITBIT_TOKEN_FILE", "fitbit/token_store.json"))
TOKEN_URL = "https://api.fitbit.com/oauth2/token"
CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET")
REDIRECT_URI = os.getenv("FITBIT_REDIRECT_URI", "https://localhost")

# Optional safe debug (no secrets). Enable with FITBIT_DEBUG_CONFIG=1
if os.getenv("FITBIT_DEBUG_CONFIG") == "1":
    cid_suffix = (CLIENT_ID[-4:] if CLIENT_ID else "unset")
    print(
        f"[fitbit] Debug: token_manager env: CLIENT_ID suffix={cid_suffix}, redirect={REDIRECT_URI}, token_file={Path(os.getenv('FITBIT_TOKEN_FILE', 'fitbit/token_store.json')).as_posix()}"
    )

class TokenError(Exception):
    pass

def load_tokens():
    if TOKEN_FILE.exists():
        try:
            return json.loads(TOKEN_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_tokens(tokens: dict):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))

def is_expired(tokens: dict, skew_seconds: int = 120) -> bool:
    """Return True if token is expired or close to expiry (with skew)."""
    exp = tokens.get("obtained_at", 0) + tokens.get("expires_in", 0)
    return (time.time() + skew_seconds) >= exp

def refresh_access_token(tokens: dict) -> dict:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise TokenError("FITBIT_CLIENT_ID/SECRET not set in environment")
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise TokenError("No refresh_token available; re-authorize")

    basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
    }
    resp = requests.post(TOKEN_URL, headers=headers, data=data)
    if resp.status_code != 200:
        raise TokenError(f"Refresh failed: {resp.status_code} {resp.text}")
    new_tokens = resp.json()
    # Merge and persist
    merged = {
        **tokens,
        **new_tokens,
        "obtained_at": int(time.time()),
    }
    save_tokens(merged)
    return merged

from typing import Optional, Tuple

def ensure_access_token() -> Tuple[Optional[str], Optional[str]]:
    """Return (access_token, user_id), refreshing if needed. Tokens must exist in TOKEN_FILE."""
    tokens = load_tokens()
    if not tokens:
        raise TokenError("No tokens found. Run fitbit/get_fitbit_token.py first and then save tokens to token_store.json")
    if tokens.get("obtained_at") is None:
        # Assume freshly created elsewhere; stamp now if missing
        tokens["obtained_at"] = int(time.time())
        save_tokens(tokens)
    if is_expired(tokens):
        tokens = refresh_access_token(tokens)
    return tokens.get("access_token"), tokens.get("user_id")

# --- Participant-aware helper ---
from typing import Union

def ensure_access_token_from(token_file: Union[str, Path]) -> Tuple[Optional[str], Optional[str]]:
    """Like ensure_access_token, but using a specific token file path (per-participant)."""
    global TOKEN_FILE
    old = TOKEN_FILE
    try:
        TOKEN_FILE = Path(token_file)
        return ensure_access_token()
    finally:
        TOKEN_FILE = old