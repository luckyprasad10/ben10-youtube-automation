import os
import json
from pathlib import Path
from typing import Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from src.config import (
    YOUTUBE_CLIENT_ID,
    YOUTUBE_CLIENT_SECRET,
    YOUTUBE_REFRESH_TOKEN,
    CLIENT_SECRETS_FILE,
    TOKEN_FILE,
    ROOT_DIR
)

# YouTube Data API upload and management scopes
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def get_authenticated_service():
    """
    Returns an authenticated YouTube Data API v3 service resource.
    Supports both headless cloud environment (via REFRESH_TOKEN) and local interactive flow.
    """
    creds: Optional[Credentials] = None

    # Priority 1: Environment Variables (GitHub Secrets / .env for Headless Cloud)
    client_id = os.getenv("YOUTUBE_CLIENT_ID") or YOUTUBE_CLIENT_ID
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET") or YOUTUBE_CLIENT_SECRET
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN") or YOUTUBE_REFRESH_TOKEN

    if client_id and client_secret and refresh_token:
        creds = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES
        )
        try:
            creds.refresh(Request())
            return build("youtube", "v3", credentials=creds)
        except Exception as e:
            print(f"[YouTube Auth] Error refreshing token from environment: {e}")

    # Priority 2: Saved token.json file
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            if creds and creds.valid:
                return build("youtube", "v3", credentials=creds)
        except Exception as e:
            print(f"[YouTube Auth] token.json invalid or expired: {e}")

    # Priority 3: Interactive OAuth Consent (Local Setup)
    if CLIENT_SECRETS_FILE.exists():
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save token for future headless runs
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
            
        print("\n" + "="*60)
        print("🎉 YouTube Authentication Successful!")
        print(f"Refresh Token: {creds.refresh_token}")
        print("Save this refresh token in your .env or GitHub Secrets:")
        print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
        print("="*60 + "\n")
        
        return build("youtube", "v3", credentials=creds)

    raise ValueError(
        "[YouTube Auth] No valid credentials found! "
        "Please provide client_secret.json or configure YOUTUBE_CLIENT_ID, "
        "YOUTUBE_CLIENT_SECRET, and YOUTUBE_REFRESH_TOKEN in your .env file."
    )

if __name__ == "__main__":
    print("[YouTube Auth] Running interactive authorization setup...")
    try:
        service = get_authenticated_service()
        channels = service.channels().list(mine=True, part="snippet").execute()
        for ch in channels.get("items", []):
            print(f"Connected to YouTube Channel: {ch['snippet']['title']} ({ch['id']})")
    except Exception as e:
        print(f"[YouTube Auth] Setup Error: {e}")
