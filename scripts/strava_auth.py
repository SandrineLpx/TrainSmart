"""
One-time Strava OAuth2 setup for Train Smart.

Steps:
1. Go to https://www.strava.com/settings/api and create an API application.
   - Application Name: Train Smart
   - Category: Training
   - Website: http://localhost
   - Authorization Callback Domain: localhost
2. Note your Client ID and Client Secret.
3. Run this script: python scripts/strava_auth.py
4. It will open a browser for you to authorize, then save tokens to data/strava_config.json.
"""

import http.server
import json
import os
import ssl
import threading
import urllib.parse
import urllib.request
import webbrowser

# Fix SSL certificate issues on Windows
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()
    SSL_CONTEXT.check_hostname = False
    SSL_CONTEXT.verify_mode = ssl.CERT_NONE

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "strava_config.json")

auth_code = None
server_ready = threading.Event()


class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<h1>Authorization successful!</h1>"
                b"<p>You can close this tab and return to the terminal.</p>"
            )
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed.")

    def log_message(self, format, *args):
        pass  # Suppress server logs


def main():
    client_id = input("Enter your Strava Client ID: ").strip()
    client_secret = input("Enter your Strava Client Secret: ").strip()

    # Start local server to catch the redirect
    server = http.server.HTTPServer(("localhost", 8484), OAuthHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    # Open browser for authorization
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri=http://localhost:8484"
        f"&scope=activity:read_all"
    )
    print(f"\nOpening browser for authorization...")
    print(f"If it doesn't open, go to: {auth_url}\n")
    webbrowser.open(auth_url)

    # Wait for the callback
    thread.join(timeout=120)

    if not auth_code:
        print("ERROR: Did not receive authorization code. Try again.")
        return

    print(f"Got authorization code. Exchanging for tokens...")

    # Exchange code for tokens
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request(
        "https://www.strava.com/oauth/token", data=data, method="POST"
    )
    with urllib.request.urlopen(req, context=SSL_CONTEXT) as resp:
        token_data = json.loads(resp.read())

    config = {
        "client_id": client_id,
        "client_secret": client_secret,
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "expires_at": token_data["expires_at"],
    }

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"\nTokens saved to {CONFIG_PATH}")
    print(f"Athlete: {token_data.get('athlete', {}).get('firstname', 'Unknown')}")
    print("Setup complete! The Strava MCP server is now ready to use.")


if __name__ == "__main__":
    main()
