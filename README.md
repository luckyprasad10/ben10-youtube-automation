# ⚡ Ben 10 to YouTube & Instagram Cloud Automation Suite

An enterprise-grade, fully automated AI-driven pipeline designed for **@krylox ai** to ingest Ben 10 episodes in sequence from Google Drive, apply protective Content ID transformations, generate viral SEO metadata and high-CTR thumbnails using **Gemini**, and upload simultaneously to **YouTube** (Full Episodes & Shorts) and **Instagram** (Reels) 24/7 on a cloud schedule.

---

## 🚀 Key Features

- **Multi-Platform Distribution (YouTube + Instagram)**:
  - **YouTube**: Ingests and uploads full transformed episodes and 60-second viral Shorts.
  - **Instagram**: Automatically publishes 9:16 vertical high-action Reels with viral captions, call-to-actions, and top hashtags.
- **Sequential Canon Tracker (`tracker.py`)**:
  - Automatically indexes all 348 episodes across *Classic, Alien Force, Ultimate Alien, Omniverse, Reboot, and Movies*.
  - Ensures episodes are processed strictly in chronological order without duplication.
- **AI Brain (`ai_metadata.py`)**:
  - Generates curiosity-driven Hindi/English titles with emojis.
  - Generates comprehensive SEO descriptions with timestamps, character lore, traffic funnel links, and legal Fair Use disclaimers.
  - High search-volume tag generator.
- **High-CTR Thumbnail Studio (`thumbnail_generator.py`)**:
  - Extracts sharpest action keyframes using FFmpeg.
  - Applies 1280x720 16:9 framing, cartoon contrast/saturation boost, signature Ben 10 Neon-Green border glow, season/episode pill badges, and bold yellow hook typography.
- **Anti-Content ID Shield (`video_processor.py`)**:
  - Modulates audio pitch/tempo (+2%) and frequency curves to prevent automated audio fingerprint matching.
  - Boosts video contrast/saturation and applies watermark.
  - Generates 9:16 vertical (1080x1920) viral Shorts/Reels with blurred background padding.
- **Traffic Funnel & Monetization Engine**:
  - Pins top-level comment and Instagram bio CTAs directing viewers to your Telegram channel / TeraBox / CPA link shorteners to generate cash flow from day 1.
- **24/7 Autonomous Cloud Runner**:
  - Uses GitHub Actions cron workflows — completely free, running on cloud servers without needing your PC to stay on.

---

## 📁 Project Structure

```
Ben 10 to YT/
├── .github/workflows/
│   └── upload_pipeline.yml       # Cloud Cron automation (runs 2x daily on GitHub Actions)
├── src/
│   ├── __init__.py
│   ├── config.py                 # Central configuration & FFmpeg resolver
│   ├── tracker.py                # Chronological Drive indexer & state.json manager
│   ├── downloader.py             # Single-file streaming downloader & cleaner
│   ├── ai_metadata.py            # Gemini SEO title, description & tag engine
│   ├── video_processor.py        # Anti-Claim filter & 9:16 Shorts/Reels generator
│   ├── thumbnail_generator.py    # Pillow-based high-CTR thumbnail studio
│   ├── youtube_auth.py           # OAuth 2.0 credential & token manager
│   ├── youtube_uploader.py       # Resumable YouTube Data API v3 uploader
│   └── instagram_uploader.py     # instagrapi-powered Instagram Reels uploader & session cache
├── pipeline.py                   # Master CLI controller
├── state.json                    # Tracking database of all 348 episodes
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment secrets template
└── .gitignore                    # Protects API keys and tokens from git
```

---

## 🔑 Credentials Setup

### 1. YouTube Data API v3 (One-Time Setup in 2 Minutes)
1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `Krylox-AI-YouTube`).
3. Search for **YouTube Data API v3** and click **Enable**.
4. Go to **APIs & Services > Credentials** -> **Create Credentials** -> **OAuth client ID** (Application type: **Desktop app**).
5. Download JSON and save it as `client_secret.json` in this project directory.
6. Run:
   ```bash
   python -m src.youtube_auth
   ```
7. Approve with your YouTube account. Save the printed `YOUTUBE_REFRESH_TOKEN`.

### 2. Instagram Credentials
In your `.env` (or GitHub Secrets for cloud deployment):
```env
ENABLE_INSTAGRAM_UPLOAD=true
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```
*(Session is automatically cached in `ig_session.json` to avoid login challenges).*

---

## 🖥️ Local Usage

### Scan and Index All Episodes
```bash
python pipeline.py --scan
```

### Check Upload Statistics (YouTube + Instagram)
```bash
python pipeline.py --status
```

### Test with Dry Run (Safe Test - No Upload)
```bash
python pipeline.py --run-next --mode both --instagram --dry-run
```

### Run Live Upload (YouTube + Instagram)
```bash
python pipeline.py --run-next --mode both --instagram --privacy unlisted
```

---

## ☁️ Cloud Deployment via GitHub Actions (Runs Automatically)

1. Create a **Private** repository on your GitHub account (`luckyprasad10/ben10-youtube-automation`).
2. Push this project to GitHub using the bundled Git:
   ```bash
   .\bin\git\cmd\git.exe remote add origin https://github.com/luckyprasad10/ben10-youtube-automation.git
   .\bin\git\cmd\git.exe branch -M main
   .\bin\git\cmd\git.exe push -u origin main
   ```
3. In GitHub, navigate to **Settings > Secrets and variables > Actions > New repository secret**.
4. Add the following repository secrets:
   - `GEMINI_API_KEY`: Your Google AI Studio API key.
   - `YOUTUBE_CLIENT_ID`: OAuth Client ID from Google Cloud.
   - `YOUTUBE_CLIENT_SECRET`: OAuth Client Secret from Google Cloud.
   - `YOUTUBE_REFRESH_TOKEN`: The refresh token generated by `youtube_auth.py`.
   - `INSTAGRAM_USERNAME`: Your Instagram account username.
   - `INSTAGRAM_PASSWORD`: Your Instagram account password.
   - `ENABLE_INSTAGRAM_UPLOAD`: `true`
   - `TELEGRAM_CHANNEL_URL`: Your Telegram channel or monetization link.
   - `MONETIZATION_DOWNLOAD_URL`: Your monetization download link.
5. In GitHub, go to **Settings > Actions > General > Workflow permissions** and select **Read and write permissions**.
6. **Done!** The cloud workflow runs automatically twice every day, uploads the next episode in sequence to YouTube and Instagram simultaneously, and records progress in `state.json`.
