import os
import json
import time
from pathlib import Path
from typing import Optional
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

from src.config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    INSTAGRAM_SESSION_FILE,
    INSTAGRAM_HANDLE,
    TELEGRAM_CHANNEL_URL,
    MONETIZATION_DOWNLOAD_URL
)

class InstagramReelUploader:
    def __init__(
        self,
        username: str = INSTAGRAM_USERNAME,
        password: str = INSTAGRAM_PASSWORD,
        session_file: Path = INSTAGRAM_SESSION_FILE
    ):
        self.username = username
        self.password = password
        self.session_file = session_file
        self.cl = Client()
        self.cl.delay_range = [2, 5]

    def authenticate(self) -> bool:
        """Authenticates with Instagram using cached session or credentials."""
        if not self.username or not self.password:
            print("[Instagram] Error: INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD not configured.")
            return False

        # Priority 1: Reuse existing session
        if self.session_file.exists():
            print(f"[Instagram] Loading cached session from {self.session_file.name}...")
            try:
                self.cl.load_settings(str(self.session_file))
                self.cl.login(self.username, self.password)
                self.cl.get_timeline_feed()
                print(f"[Instagram] ✅ Successfully authenticated via cached session as @{self.username}!")
                return True
            except Exception as e:
                print(f"[Instagram] Cached session invalid/expired ({e}). Performing clean login...")

        # Priority 2: Fresh credential login
        try:
            print(f"[Instagram] Logging into Instagram as @{self.username}...")
            self.cl.login(self.username, self.password)
            self.cl.dump_settings(str(self.session_file))
            print(f"[Instagram] ✅ Logged in successfully! Session cached to {self.session_file.name}")
            return True
        except Exception as e:
            print(f"[Instagram] ❌ Login failed: {e}")
            return False

    def generate_reel_caption(self, series: str, season: int, episode: int, hook_text: str) -> str:
        """Generates viral Instagram Reel caption with hooks, call-to-action & hashtags."""
        hashtags = [
            "#ben10", "#omnitrix", "#cartoonnetwork", "#ben10classic",
            "#alienforce", "#omniverse", "#alienx", "#nostalgia",
            "#reelsindia", "#viralreels", "#explorepage", "#cartoons",
            "#hindi"
        ]
        caption = f"""⚡ {hook_text} | {series} S{season:02d}E{episode:02d} 🔥

Nostalgia hits hard! Who is your favorite alien from Ben 10? Comment below! 👇

🔥 Watch & Download All Uncut Ben 10 Episodes in Full HD:
👉 Link in Bio! (or join our Telegram: {TELEGRAM_CHANNEL_URL})

Follow {INSTAGRAM_HANDLE} for daily Ben 10 epic battles & alien transformations! 👽

.
.
{' '.join(hashtags)}
"""
        return caption.strip()

    def upload_reel(
        self,
        video_path: Path,
        caption: str,
        thumbnail_path: Optional[Path] = None
    ) -> Optional[str]:
        """Uploads a 9:16 video as an Instagram Reel."""
        if not self.authenticate():
            return None

        print(f"[Instagram] Uploading Reel from {video_path.name}...")
        try:
            media = self.cl.clip_upload(
                path=video_path,
                caption=caption,
                thumbnail=thumbnail_path if (thumbnail_path and thumbnail_path.exists()) else None
            )
            media_code = getattr(media, "code", None) or getattr(media, "pk", "")
            reel_url = f"https://www.instagram.com/reel/{media_code}/" if media_code else "Uploaded"
            print(f"[Instagram] 🎉 Reel published successfully! URL: {reel_url}")
            return reel_url
        except Exception as e:
            print(f"[Instagram] ❌ Error uploading reel: {e}")
            return None
