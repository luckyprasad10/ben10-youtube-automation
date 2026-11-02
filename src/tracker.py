import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional
import gdown

from src.config import STATE_FILE, DRIVE_FOLDER_URL

SERIES_ORDER = [
    "Ben10 Classic",
    "Ben10 Alien Force",
    "Ben 10 Ultimate Alien",
    "Ben 10 Omniverse",
    "Ben 10 Reboot",
    "Movies"
]

def parse_episode_metadata(filepath: str) -> Dict:
    """Extracts series, season, episode and clean name from relative path."""
    norm = os.path.normpath(filepath)
    parts = norm.split(os.sep)
    
    series = "Ben 10"
    for s in SERIES_ORDER:
        if s.lower() in norm.lower():
            series = s
            break
            
    filename = parts[-1]
    
    # Try S01E01 pattern
    se_match = re.search(r'S(\d+)[._-]?E(\d+)', filename, re.IGNORECASE)
    if se_match:
        season = int(se_match.group(1))
        episode = int(se_match.group(2))
    else:
        # Try Ep pattern
        ep_match = re.search(r'(?:Episode|Ep)[._-]?(\d+)', filename, re.IGNORECASE)
        episode = int(ep_match.group(1)) if ep_match else 1
        s_match = re.search(r'Season[._-]?(\d+)|S(\d+)', norm, re.IGNORECASE)
        season = int(s_match.group(1) or s_match.group(2)) if s_match else 1

    series_priority = 99
    for idx, s in enumerate(SERIES_ORDER):
        if s.lower() == series.lower():
            series_priority = idx
            break

    return {
        "series": series,
        "series_priority": series_priority,
        "season": season,
        "episode": episode,
        "filename": filename,
        "clean_name": filename.replace("_", " ").replace(".mkv", "").replace(".mp4", "")
    }

class DriveTracker:
    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self.items: List[Dict] = []
        self.load_state()

    def load_state(self):
        """Loads state from file if exists."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
            except Exception as e:
                print(f"[Tracker] Error loading state.json: {e}")
                self.items = []

    def save_state(self):
        """Saves current state to file."""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.items, f, indent=2, ensure_ascii=False)

    def scan_drive(self) -> int:
        """Scans Google Drive folder and indexes/sorts all videos."""
        print(f"[Tracker] Scanning Drive folder {DRIVE_FOLDER_URL}...")
        files = gdown.download_folder(DRIVE_FOLDER_URL, quiet=True, skip_download=True)
        if not files:
            print("[Tracker] No files discovered or folder unreachable.")
            return 0

        existing_ids = {item["id"]: item for item in self.items}
        new_items = []

        for f in files:
            meta = parse_episode_metadata(f.path)
            file_id = f.id
            if file_id in existing_ids:
                # Keep existing progress
                item = existing_ids[file_id]
                item.update(meta)
                new_items.append(item)
            else:
                new_items.append({
                    "id": file_id,
                    "drive_path": f.path,
                    "series": meta["series"],
                    "series_priority": meta["series_priority"],
                    "season": meta["season"],
                    "episode": meta["episode"],
                    "filename": meta["filename"],
                    "clean_name": meta["clean_name"],
                    "status": "pending",
                    "uploaded_full": False,
                    "uploaded_short": False,
                    "youtube_full_id": None,
                    "youtube_short_id": None,
                    "last_processed": None
                })

        # Sort in canonical sequential order
        new_items.sort(key=lambda x: (x["series_priority"], x["season"], x["episode"], x["filename"]))

        self.items = new_items
        self.save_state()
        print(f"[Tracker] Successfully indexed {len(self.items)} episodes in chronological sequence.")
        return len(self.items)

    def get_next_episode(self, mode: str = "full") -> Optional[Dict]:
        """Returns the next un-uploaded episode according to chronological sequence."""
        if not self.items:
            self.scan_drive()

        for item in self.items:
            if mode == "full" and not item.get("uploaded_full"):
                return item
            elif mode == "short" and not item.get("uploaded_short"):
                return item
        return None

    def mark_completed(self, file_id: str, mode: str, youtube_id: str):
        """Marks an episode as successfully processed and uploaded."""
        for item in self.items:
            if item["id"] == file_id:
                if mode == "full":
                    item["uploaded_full"] = True
                    item["youtube_full_id"] = youtube_id
                elif mode == "short":
                    item["uploaded_short"] = True
                    item["youtube_short_id"] = youtube_id
                import datetime
                item["last_processed"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                item["status"] = "completed" if (item.get("uploaded_full") and item.get("uploaded_short")) else "in_progress"
                break
        self.save_state()
