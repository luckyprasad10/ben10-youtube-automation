import os
import sys
import re
import subprocess
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

ROOT_DIR = Path(__file__).resolve().parent
CLIENT_SECRETS_FILE = ROOT_DIR / "client_secret.json"
TOKEN_FILE = ROOT_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRETS_FILE),
        scopes=SCOPES,
        redirect_uri="http://localhost:8080/"
    )
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    print("\n" + "="*70)
    print("🔑 GOOGLE AUTHORIZATION LINK:")
    print("="*70)
    print(auth_url)
    print("="*70 + "\n")

    # Launch Chrome directly to the authorization link
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    if os.path.exists(chrome_path):
        subprocess.Popen([chrome_path, auth_url])
    else:
        import webbrowser
        webbrowser.open(auth_url)

    # Listen on localhost:8080
    creds = flow.run_local_server(port=8080, open_browser=False)

    # Save token.json
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    # Update .env
    if creds.refresh_token:
        env_path = ROOT_DIR / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                text = f.read()
            text = re.sub(r"YOUTUBE_REFRESH_TOKEN=.*", f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}", text)
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(text)

    print("\n🎉 YOUTUBE AUTHORIZATION SUCCESSFUL!")
    print(f"Refresh Token: {creds.refresh_token}")
    print("Saved to .env and token.json!\n")

if __name__ == "__main__":
    main()

