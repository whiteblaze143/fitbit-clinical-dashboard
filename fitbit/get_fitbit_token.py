import base64
import os
import sys
import urllib.parse
import webbrowser
import requests
import time
import json
from pathlib import Path
try:
    # Load .env early to make FITBIT_* available to config getters
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading
try:
    from fitbit.config import get_client_id, get_client_secret, get_redirect_uri, get_scopes
except Exception:
    try:
        from .config import get_client_id, get_client_secret, get_redirect_uri, get_scopes
    except Exception:
        from config import get_client_id, get_client_secret, get_redirect_uri, get_scopes
import secrets
import argparse
CLIENT_ID = get_client_id()
CLIENT_SECRET = get_client_secret()
REDIRECT_URI = get_redirect_uri()
SCOPES = get_scopes()
AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"

DEFAULT_TOKEN_FILE = Path(os.getenv("FITBIT_TOKEN_FILE", "fitbit/token_store.json"))

if not CLIENT_ID or not CLIENT_SECRET:
    print("Missing FITBIT_CLIENT_ID or FITBIT_CLIENT_SECRET in environment.")
    sys.exit(1)

class CallbackHandler(BaseHTTPRequestHandler):
    code = None
    # default to empty string to simplify type expectations
    expected_state = ""
    def do_GET(self):
        # Fitbit returns either as query (?code=) or fragment (#access_token=) depending on flow
        # We support Authorization Code flow here (query param)
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if 'code' in params:
            # CSRF state check
            state = params.get('state', [None])[0]
            if CallbackHandler.expected_state and state != CallbackHandler.expected_state:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Invalid state parameter. Aborting.")
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            CallbackHandler.code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization successful. You can close this window.")
            # Shutdown server asynchronously to avoid deadlock inside handler
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"No code found. Ensure app is configured for Authorization Code flow and redirect URI matches.")
            threading.Thread(target=self.server.shutdown, daemon=True).start()


def main():
    parser = argparse.ArgumentParser(description="Authorize Fitbit and save tokens per participant")
    parser.add_argument("--participant", dest="participant", help="studyId to save tokens under fitbit/tokens/<studyId>.json")
    parser.add_argument("--token-file", dest="token_file", help="Explicit token file path to save tokens")
    args = parser.parse_args()
    # NOTE: PKCE could be added here for extra security even for public clients.
    # For server-type apps, Basic auth with client secret is acceptable per Fitbit docs.
    csrf_state = secrets.token_urlsafe(24)
    # Optional safe debug (no secrets)
    if os.getenv("FITBIT_DEBUG_CONFIG") == "1":
        cid = CLIENT_ID or ""
        cid_suffix = cid[-4:] if cid else "unset"
        try:
            scopes_count = len((SCOPES or "").split())
        except Exception:
            scopes_count = 0
        print(f"[fitbit] Debug: CLIENT_ID suffix={cid_suffix}, redirect={REDIRECT_URI}, scopes_words={scopes_count}")

    # Build auth URL
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": csrf_state,
        "expires_in": "31536000",
        "prompt": "consent"
    }
    auth_url = f"{AUTH_URL}?" + urllib.parse.urlencode(params)
    print("Opening browser for Fitbit authorization...")
    print(auth_url)
    # Open browser
    webbrowser.open(auth_url)

    # Start local server derived from REDIRECT_URI if scheme is http and host is localhost
    parsed_redirect = urlparse(REDIRECT_URI)
    host = parsed_redirect.hostname or "localhost"
    port = parsed_redirect.port or (8080 if parsed_redirect.scheme == "http" else 443)
    path = parsed_redirect.path or "/"
    try:
        httpd = HTTPServer((host, port), CallbackHandler)
        CallbackHandler.expected_state = csrf_state
        print(f"Listening on http://{host}:{port}{path} for redirect...")
        httpd.serve_forever()
    except OSError:
        print("Could not bind local server; if you used https://localhost, copy the 'code' from the URL and paste below.")

    code = CallbackHandler.code or input("Paste the 'code' parameter from the redirected URL: ").strip()

    # Exchange code for tokens
    basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    print("Exchanging authorization code for tokens...")
    resp = requests.post(TOKEN_URL, headers=headers, data=data)
    if resp.status_code != 200:
        print("Token exchange failed:", resp.status_code, resp.text)
        sys.exit(1)
    tokens = resp.json()
    # Persist tokens to file with obtained_at for refresh tracking
    tokens["obtained_at"] = int(time.time())
    # Resolve destination token file
    token_path = None
    if args.token_file:
        token_path = Path(args.token_file)
    elif args.participant:
        token_path = Path("fitbit") / "tokens" / f"{args.participant}.json"
    else:
        token_path = DEFAULT_TOKEN_FILE
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(json.dumps(tokens, indent=2))
    print(f"Saved tokens to {token_path}")
    # Do not print tokens to stdout; show user id for confirmation
    print("User ID:", tokens.get("user_id"))

if __name__ == "__main__":
    main()
