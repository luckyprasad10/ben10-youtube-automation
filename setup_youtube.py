import os
import sys
import time
import shutil
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DOWNLOADS_USER_DIR = Path.home() / "Downloads"

def launch_setup():
    print("\n" + "="*70)
    print("🚀 AUTOMATED YOUTUBE API SETUP ASSISTANT")
    print("="*70)
    print("\nBecause Google security prevents automated password entry (to protect")
    print("your account from being locked), we are opening the exact Google Cloud")
    print("Console pages in your Chrome browser where you are already signed in.\n")

    # Step 1: Open YouTube Data API Enable Page
    api_url = "https://console.cloud.google.com/apis/library/youtube.googleapis.com"
    print("1️⃣ Opening YouTube Data API page in Chrome...")
    print(f"   URL: {api_url}")
    print("   👉 Click 'ENABLE' if it asks you to enable the API.\n")
    webbrowser.open(api_url)
    
    time.sleep(4)

    # Step 2: Open Create OAuth Credentials Page
    cred_url = "https://console.cloud.google.com/apis/credentials/oauthclient"
    print("2️⃣ Opening Create OAuth Client ID page in Chrome...")
    print(f"   URL: {cred_url}")
    print("   👉 Select Application Type: 'Desktop app'")
    print("   👉 Click 'CREATE' and then 'DOWNLOAD JSON'.\n")
    webbrowser.open(cred_url)

    print("="*70)
    print("👀 Watching your Downloads folder for the downloaded client_secret JSON...")
    print("   (Save it anywhere or in Downloads, the assistant will detect it instantly)")
    print("="*70 + "\n")

    detected_file = None
    target_dest = ROOT_DIR / "client_secret.json"

    # Poll for 120 seconds
    for _ in range(60):
        # Check current folder
        if target_dest.exists() and target_dest.stat().st_size > 50:
            detected_file = target_dest
            break

        # Check Downloads folder
        if DOWNLOADS_USER_DIR.exists():
            candidates = list(DOWNLOADS_USER_DIR.glob("client_secret*.json"))
            if candidates:
                # Get newest file
                newest = max(candidates, key=os.path.getmtime)
                # Check if it was modified in the last 15 minutes
                if (time.time() - os.path.getmtime(newest)) < 900:
                    shutil.copy(newest, target_dest)
                    detected_file = target_dest
                    print(f"✅ Found in Downloads: {newest.name}")
                    print(f"✅ Automatically copied to: {target_dest.name}")
                    break
        time.sleep(2)

    if detected_file and detected_file.exists():
        print("\n🎉 client_secret.json successfully detected!")
        print("Now opening Google account authorization window...")
        from src.youtube_auth import get_authenticated_service
        try:
            get_authenticated_service()
            print("\n🎉 YOUTUBE SETUP COMPLETE! Everything is ready to upload.")
        except Exception as e:
            print(f"Auth error: {e}")
    else:
        print("\n⏳ Setup assistant timed out waiting for the JSON file.")
        print(f"Once downloaded, simply place it as '{target_dest}' and run:")
        print("python -m src.youtube_auth")

if __name__ == "__main__":
    launch_setup()

