import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Directories
DOWNLOADS_DIR = ROOT_DIR / "downloads"
OUTPUT_DIR = ROOT_DIR / "output"
TEMP_DIR = ROOT_DIR / "temp"
STATE_FILE = ROOT_DIR / "state.json"

for d in [DOWNLOADS_DIR, OUTPUT_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Google AI & Drive Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "1qUUMEioaCH-LiWTYNwFmADLNF73JRE5N")
DRIVE_FOLDER_URL = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"

# Channel & Brand Identity
CHANNEL_HANDLE = os.getenv("CHANNEL_HANDLE", "@krylox ai")
CONTENT_MODE = os.getenv("CONTENT_MODE", "both")  # 'full', 'short', or 'both'
DEFAULT_PRIVACY_STATUS = os.getenv("DEFAULT_PRIVACY_STATUS", "unlisted")

# Monetization Links
TELEGRAM_CHANNEL_URL = os.getenv("TELEGRAM_CHANNEL_URL", "https://t.me/krylox_ai")
MONETIZATION_DOWNLOAD_URL = os.getenv("MONETIZATION_DOWNLOAD_URL", "https://t.me/krylox_ai")

# YouTube API Credentials
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
CLIENT_SECRETS_FILE = ROOT_DIR / "client_secret.json"
TOKEN_FILE = ROOT_DIR / "token.json"

# Resolve FFmpeg Executable
def get_ffmpeg_executable() -> str:
    """Finds system ffmpeg or falls back to imageio_ffmpeg bundled binary."""
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

FFMPEG_EXE = get_ffmpeg_executable()
