import os
import shutil
from pathlib import Path
from typing import Optional
import gdown

from src.config import DOWNLOADS_DIR

def download_episode(file_id: str, filename: str) -> Optional[Path]:
    """Downloads a single video file by Drive file ID."""
    clean_name = filename.replace(" ", "_")
    output_path = DOWNLOADS_DIR / clean_name
    
    if output_path.exists() and output_path.stat().st_size > 1024 * 1024:
        print(f"[Downloader] File already downloaded: {output_path} ({output_path.stat().st_size // (1024*1024)} MB)")
        return output_path

    print(f"[Downloader] Downloading {filename} (ID: {file_id})...")
    url = f"https://drive.google.com/uc?id={file_id}"
    
    try:
        downloaded = gdown.download(id=file_id, output=str(output_path), quiet=False)
        if downloaded and os.path.exists(downloaded) and os.path.getsize(downloaded) > 1024:
            print(f"[Downloader] Successfully downloaded: {downloaded} ({os.path.getsize(downloaded) // (1024*1024)} MB)")
            return Path(downloaded)
        else:
            print(f"[Downloader] Download produced empty or missing file.")
            return None
    except Exception as e:
        print(f"[Downloader] Error during download: {e}")
        return None

def cleanup_file(path: Path):
    """Deletes downloaded or processed video file to preserve cloud disk space."""
    try:
        if path and path.exists():
            path.unlink()
            print(f"[Downloader] Cleaned up temporary file: {path.name}")
    except Exception as e:
        print(f"[Downloader] Failed to delete {path}: {e}")
