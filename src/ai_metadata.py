import json
import urllib.request
from typing import Dict
from src.config import GEMINI_API_KEY, CHANNEL_HANDLE, TELEGRAM_CHANNEL_URL, MONETIZATION_DOWNLOAD_URL

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"

def generate_video_metadata(series: str, season: int, episode: int, filename: str, is_short: bool = False) -> Dict:
    """Uses Gemini to generate high-CTR SEO title, description, tags, and thumbnail text with robust local fallback."""
    if not GEMINI_API_KEY:
        print("[AI Metadata] Warning: No GEMINI_API_KEY found, using standard template.")
        return get_fallback_metadata(series, season, episode, is_short)

    prompt = f"""
You are an expert YouTube SEO and viral content strategist managing the channel '{CHANNEL_HANDLE}'.
Create high-CTR YouTube metadata for a Ben 10 video in Hindi/English mixed audience:

Series: {series}
Season: {season}
Episode: {episode}
Filename: {filename}
Format: {'YouTube 60-Second Short' if is_short else 'Full Episode / Highlight'}

Return STRICTLY a JSON object with the following keys (no markdown code blocks, just raw JSON):
{{
  "title": "High-CTR, curiosity-driven title under 95 characters with emojis and Hindi keywords (e.g. '🔥 Ben 10 Omniverse Ep 1: The New Omnitrix Revealed! | Hindi Dubbed')",
  "description": "Engaging 3-paragraph description. Include episode plot synopsis, key alien appearances, affiliate/traffic notice, and a polite Fair Use copyright disclaimer.",
  "tags": ["15-20 comma separated high-search-volume tags for Ben 10 in Hindi, cartoon network, omniverse, alien force, etc."],
  "thumbnail_text": "3 to 4 big punchy words for the thumbnail overlay (e.g. 'NEW OMNITRIX?!' or 'ALIEN X POWER')",
  "pinned_comment": "Curiosity hook directing viewers to download/watch all uncut episodes on our Telegram/link"
}}
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }

    url = f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidate = data.get("candidates", [])[0]
            text = candidate["content"]["parts"][0]["text"]
            meta = json.loads(text)
            
            # Inject channel links and disclaimers
            funnel_text = f"\n\n🔥 Watch & Download All Uncut Ben 10 Episodes in Full HD:\n👉 {MONETIZATION_DOWNLOAD_URL}\n👉 Join Telegram: {TELEGRAM_CHANNEL_URL}\n\nSubscribe to {CHANNEL_HANDLE} for daily episodes and epic alien moments!"
            disclaimer = "\n\n⚠️ Disclaimer: Copyright Disclaimer under section 107 of the Copyright Act 1976, allowance is made for 'fair use' for purposes such as criticism, comment, news reporting, teaching, scholarship, education and research. All rights belong to Cartoon Network / Warner Bros. Discovery."
            
            meta["description"] = meta.get("description", "") + funnel_text + disclaimer
            meta["pinned_comment"] = f"🔥 Download all episodes in Hindi HD here: {MONETIZATION_DOWNLOAD_URL} | Join Telegram: {TELEGRAM_CHANNEL_URL}"
            return meta

    except Exception as e:
        print(f"[AI Metadata] Gemini API notice: ({e}). Applying optimized SEO metadata templates.")
        return get_fallback_metadata(series, season, episode, is_short)

def get_fallback_metadata(series: str, season: int, episode: int, is_short: bool) -> Dict:
    """Robust fallback metadata generator when offline or API limit reached."""
    fmt_title = f"⚡ {series} Season {season} Episode {episode} | Full Action In Hindi Dubbed 🔥"
    if is_short:
        fmt_title = f"🔥 {series} Best Alien Transformation Moment #Shorts"

    desc = f"""Welcome to {CHANNEL_HANDLE}!
Watch {series} Season {season} Episode {episode} featuring Ben Tennyson and the Omnitrix!

🔥 Watch & Download All Uncut Ben 10 Episodes in Full HD:
👉 {MONETIZATION_DOWNLOAD_URL}
👉 Join our Telegram: {TELEGRAM_CHANNEL_URL}

Subscribe to {CHANNEL_HANDLE} for daily Ben 10 episodes and epic alien action!

⚠️ Disclaimer: Copyright Disclaimer under section 107 of the Copyright Act 1976, allowance is made for 'fair use' for purposes such as criticism, comment, news reporting, teaching, scholarship, education and research. All rights belong to Cartoon Network / Warner Bros. Discovery.
"""
    return {
        "title": fmt_title[:95],
        "description": desc,
        "tags": [
            series, f"{series} Hindi", f"{series} Season {season}", f"{series} Episode {episode}",
            "Ben 10 full episode", "Ben 10 in Hindi", "Ben 10 Cartoon Network",
            "Omnitrix", "Ben 10 hindi dubbed", "Cartoon Hindi", "Krylox AI"
        ],
        "thumbnail_text": f"EPISODE {episode:02d}!",
        "pinned_comment": f"🔥 Download all uncut episodes in Hindi HD here: {MONETIZATION_DOWNLOAD_URL} | Join Telegram: {TELEGRAM_CHANNEL_URL}"
    }
