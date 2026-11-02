# ⚡ Ben 10 to YouTube Cloud Automation Suite

An enterprise-grade, fully automated AI-driven pipeline designed for **@krylox ai** to ingest Ben 10 episodes in sequence from Google Drive, apply protective Content ID transformations, generate viral SEO metadata and high-CTR thumbnails using **Gemini 2.5 Flash**, and upload to YouTube 24/7 on a cloud schedule.

---

## 🚀 Key Features

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
  - Generates 9:16 vertical (1080x1920) viral Shorts with blurred background padding.
- **Traffic Funnel & Monetization Engine**:
  - Pins top-level comment directing viewers to your Telegram channel / TeraBox / CPA link shorteners to generate cash flow from day 1.
- **24/7 Autonomous Cloud Runner**:
  - Uses GitHub Actions cron workflows — completely free, running on cloud servers without needing your PC to stay on.

---

## 📁 Project Structure

```
├── .github/workflows/
│   └── upload_pipeline.yml       # Cloud Cron automation (runs 2x daily)
├── src/
│   ├── __init__.py
│   ├── config.py                 # Central configuration & FFmpeg resolver
│   ├── tracker.py                # Chronological Drive indexer & state.json manager
│   ├── downloader.py             # Single-file streaming downloader & cleaner
│   ├── ai_metadata.py            # Gemini 2.5 SEO title, description & tag engine
│   ├── video_processor.py        # Anti-Claim filter & 9:16 Shorts generator
│   ├── thumbnail_generator.py    # Pillow-based high-CTR thumbnail studio
│   ├── youtube_auth.py           # OAuth 2.0 credential & token manager
│   └── youtube_uploader.py       # Resumable YouTube Data API v3 uploader
├── pipeline.py                   # Master CLI controller
├── state.json                    # Tracking database of all 348 episodes
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment secrets template
└── .gitignore                    # Protects API keys and tokens from git
```

---

## 🔑 YouTube API Setup (One-Time Setup in 3 Minutes)

Since Google does not permit automated password logins, YouTube uploads use the official **YouTube Data API v3 OAuth 2.0**:

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `Krylox-AI-YouTube`).
3. In the search bar, search for **YouTube Data API v3** and click **Enable**.
4. Go to **APIs & Services > OAuth consent screen**:
   - Choose **External**.
   - Fill App name: `Krylox Automation`.
   - Add your email (`techgeds@gmail.com`) as developer contact.
   - Under **Test users**, add your YouTube account email (`techgeds@gmail.com`).
5. Go to **APIs & Services > Credentials**:
   - Click **Create Credentials > OAuth client ID**.
   - Application type: **Desktop app**.
   - Name: `YouTube Uploader CLI`.
   - Click **Create**, then click **Download JSON** and save it as `client_secret.json` in this folder.
6. Run the authentication script:
   ```bash
   python -m src.youtube_auth
   ```
7. A browser window will open — select your `@krylox ai` YouTube channel and click **Allow**.
8. The console will print your `refresh_token`. Save this token!

---

## 🖥️ Local Usage

### 1. Scan and Index All Episodes
```bash
python pipeline.py --scan
```

### 2. Check Channel Upload Progress
```bash
python pipeline.py --status
```

### 3. Test with Dry Run (Safe Test - No Upload)
```bash
python pipeline.py --run-next --mode both --dry-run
```

### 4. Upload Next Episode Live
```bash
python pipeline.py --run-next --mode both --privacy unlisted
```

---

## ☁️ Cloud Deployment via GitHub Actions (Runs Automatically)

1. Create a **Private** repository on your GitHub account (`luckyprasad10/ben10-youtube-automation`).
2. Push this project to GitHub:
   ```bash
   git init
   git add .
   git commit -m "feat: initial commit of Ben 10 YouTube automation suite"
   git branch -M main
   git remote add origin https://github.com/luckyprasad10/ben10-youtube-automation.git
   git push -u origin main
   ```
3. In your GitHub repository, navigate to **Settings > Secrets and variables > Actions > New repository secret**.
4. Add the following repository secrets:
   - `GEMINI_API_KEY`: Your Google AI Studio API key.
   - `YOUTUBE_CLIENT_ID`: Your OAuth Client ID from Google Cloud.
   - `YOUTUBE_CLIENT_SECRET`: Your OAuth Client Secret.
   - `YOUTUBE_REFRESH_TOKEN`: The refresh token generated by `youtube_auth.py`.
   - `TELEGRAM_CHANNEL_URL`: Your Telegram channel or monetization link.
   - `MONETIZATION_DOWNLOAD_URL`: Your monetization download link.
5. In GitHub, go to **Settings > Actions > General > Workflow permissions** and select **Read and write permissions** (so the runner can commit the updated `state.json`).
6. **Done!** The workflow will now automatically run twice every day, grab the next sequential episode, process it, upload it, and update the state without requiring your computer to be turned on.
