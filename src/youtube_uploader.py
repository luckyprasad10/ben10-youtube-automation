import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from src.config import DEFAULT_PRIVACY_STATUS

def upload_video(
    youtube,
    video_path: Path,
    title: str,
    description: str,
    tags: List[str],
    privacy_status: str = DEFAULT_PRIVACY_STATUS,
    category_id: str = "1"  # 1 = Film & Animation, 24 = Entertainment
) -> Optional[str]:
    """Uploads a video to YouTube using resumable upload chunks."""
    print(f"[Uploader] Initiating upload for: '{title}'...")
    print(f"[Uploader] File size: {video_path.stat().st_size // (1024*1024)} MB | Privacy: {privacy_status}")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:30],
            "categoryId": category_id,
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi"
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        str(video_path),
        chunksize=1024 * 1024 * 8,  # 8 MB chunks
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    retry_count = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"[Uploader] Upload progress: {int(status.progress() * 100)}%")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                retry_count += 1
                if retry_count > 5:
                    raise e
                time.sleep(5 * retry_count)
            else:
                raise e

    if response and "id" in response:
        video_id = response["id"]
        print(f"[Uploader] 🎉 Video uploaded successfully! Video ID: {video_id}")
        print(f"[Uploader] URL: https://youtu.be/{video_id}")
        return video_id
    else:
        print("[Uploader] Upload failed to return video ID.")
        return None

def set_custom_thumbnail(youtube, video_id: str, thumbnail_path: Path) -> bool:
    """Attaches custom thumbnail to the uploaded YouTube video."""
    print(f"[Uploader] Uploading custom thumbnail: {thumbnail_path.name}...")
    try:
        media = MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=media
        ).execute()
        print(f"[Uploader] ✅ Custom thumbnail successfully set for video {video_id}!")
        return True
    except HttpError as e:
        print(f"[Uploader] Failed to set thumbnail: {e}")
        return False

def pin_comment(youtube, video_id: str, comment_text: str) -> bool:
    """Posts a pinned top-level comment with monetization links."""
    print("[Uploader] Posting monetization comment...")
    try:
        body = {
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text
                    }
                }
            }
        }
        res = youtube.commentThreads().insert(part="snippet", body=body).execute()
        comment_id = res.get("id")
        print(f"[Uploader] ✅ Pinned comment posted (ID: {comment_id})")
        return True
    except Exception as e:
        print(f"[Uploader] Note: Comment posting skipped or restricted: {e}")
        return False

