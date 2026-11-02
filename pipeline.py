import argparse
import sys
from pathlib import Path
from typing import Optional

from src.config import CONTENT_MODE, DEFAULT_PRIVACY_STATUS
from src.tracker import DriveTracker
from src.downloader import download_episode, cleanup_file
from src.ai_metadata import generate_video_metadata
from src.video_processor import extract_keyframe, process_full_episode, create_viral_short
from src.thumbnail_generator import generate_high_ctr_thumbnail
from src.youtube_auth import get_authenticated_service
from src.youtube_uploader import upload_video, set_custom_thumbnail, pin_comment

def run_pipeline(
    mode: str = CONTENT_MODE,
    dry_run: bool = False,
    privacy: str = DEFAULT_PRIVACY_STATUS,
    target_id: Optional[str] = None
):
    tracker = DriveTracker()
    
    # 1. Ensure Drive state is indexed
    if not tracker.items:
        print("[Pipeline] No cached state found. Scanning Drive folder...")
        count = tracker.scan_drive()
        if count == 0:
            print("[Pipeline] Failed to index Drive folder. Exiting.")
            return

    # 2. Get next episode
    if target_id:
        episode_item = next((item for item in tracker.items if item["id"] == target_id), None)
    else:
        req_mode = "short" if mode == "short" else "full"
        episode_item = tracker.get_next_episode(mode=req_mode)

    if not episode_item:
        print("[Pipeline] 🎉 All episodes have been successfully processed and uploaded!")
        return

    series = episode_item["series"]
    season = episode_item["season"]
    episode_num = episode_item["episode"]
    filename = episode_item["filename"]
    file_id = episode_item["id"]

    print("\n" + "="*70)
    print(f"🎬 Processing Target: {series} | S{season:02d}E{episode_num:02d} - {filename}")
    print(f"Drive ID: {file_id}")
    print(f"Pipeline Mode: {mode.upper()} | Dry Run: {dry_run}")
    print("="*70 + "\n")

    # 3. Download the video file
    downloaded_path = download_episode(file_id, filename)
    if not downloaded_path or not downloaded_path.exists():
        print("[Pipeline] Download failed. Skipping this cycle.")
        return

    processed_full_path = None
    processed_short_path = None
    keyframe_path = None
    thumb_path = None

    try:
        # 4. Extract Keyframe for Thumbnail
        keyframe_path = extract_keyframe(downloaded_path)
        if not keyframe_path:
            print("[Pipeline] Warning: Keyframe extraction failed, proceeding without frame.")

        # 5. Process Full Episode if requested
        if mode in ["full", "both"]:
            print("\n--- 1. Generating AI Metadata for Full Episode ---")
            meta_full = generate_video_metadata(series, season, episode_num, filename, is_short=False)
            print(f"Title: {meta_full['title']}")
            print(f"Thumbnail Hook: {meta_full.get('thumbnail_text')}")
            
            # Generate custom high-CTR thumbnail
            if keyframe_path:
                thumb_path = generate_high_ctr_thumbnail(
                    keyframe_path=keyframe_path,
                    series=series,
                    season=season,
                    episode=episode_num,
                    hook_text=meta_full.get("thumbnail_text", f"EPISODE {episode_num}")
                )

            # Apply Anti-Content ID Shield
            processed_full_path = process_full_episode(downloaded_path)

            if dry_run:
                print("\n[Dry Run] Full Episode processing completed locally.")
                print(f"Processed file: {processed_full_path}")
                print(f"Thumbnail file: {thumb_path}")
            else:
                print("\n--- 2. Uploading Full Episode to YouTube ---")
                youtube = get_authenticated_service()
                yt_id = upload_video(
                    youtube=youtube,
                    video_path=processed_full_path,
                    title=meta_full["title"],
                    description=meta_full["description"],
                    tags=meta_full["tags"],
                    privacy_status=privacy
                )
                if yt_id:
                    if thumb_path:
                        set_custom_thumbnail(youtube, yt_id, thumb_path)
                    if meta_full.get("pinned_comment"):
                        pin_comment(youtube, yt_id, meta_full["pinned_comment"])
                    tracker.mark_completed(file_id, mode="full", youtube_id=yt_id)

        # 6. Process 60-Second Short if requested
        if mode in ["short", "both"]:
            print("\n--- 3. Generating Viral 9:16 Short ---")
            processed_short_path = create_viral_short(downloaded_path)
            meta_short = generate_video_metadata(series, season, episode_num, filename, is_short=True)
            print(f"Short Title: {meta_short['title']}")

            if dry_run:
                print("\n[Dry Run] Viral Short created locally:")
                print(f"Short video: {processed_short_path}")
            else:
                print("\n--- 4. Uploading Short to YouTube ---")
                youtube = get_authenticated_service()
                short_id = upload_video(
                    youtube=youtube,
                    video_path=processed_short_path,
                    title=meta_short["title"],
                    description=meta_short["description"],
                    tags=meta_short["tags"] + ["#Shorts", "#viral", "#ben10"],
                    privacy_status=privacy
                )
                if short_id:
                    if meta_short.get("pinned_comment"):
                        pin_comment(youtube, short_id, meta_short["pinned_comment"])
                    tracker.mark_completed(file_id, mode="short", youtube_id=short_id)

    finally:
        # 7. Cleanup disk files to maintain cloud storage limits
        print("\n--- 5. Storage Cleanup ---")
        cleanup_file(downloaded_path)
        if processed_full_path and processed_full_path != downloaded_path:
            cleanup_file(processed_full_path)
        if processed_short_path:
            cleanup_file(processed_short_path)
        if keyframe_path:
            cleanup_file(keyframe_path)
        print("[Pipeline] Temporary files cleaned up. Cycle finished successfully.\n")

def print_status():
    tracker = DriveTracker()
    total = len(tracker.items)
    full_uploaded = sum(1 for i in tracker.items if i.get("uploaded_full"))
    shorts_uploaded = sum(1 for i in tracker.items if i.get("uploaded_short"))
    pending = total - full_uploaded

    print("\n" + "="*50)
    print("📊 BEN 10 YOUTUBE PIPELINE STATUS")
    print("="*50)
    print(f"Total Indexed Episodes: {total}")
    print(f"Full Episodes Uploaded: {full_uploaded}")
    print(f"Viral Shorts Uploaded:  {shorts_uploaded}")
    print(f"Pending Next Upload:    {pending}")
    print("="*50)

    next_ep = tracker.get_next_episode("full")
    if next_ep:
        print(f"Next in queue: {next_ep['series']} S{next_ep['season']:02d}E{next_ep['episode']:02d} ({next_ep['filename']})")
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Automated Ben 10 to YouTube Upload Pipeline")
    parser.add_argument("--scan", action="store_true", help="Scan Google Drive and update state.json")
    parser.add_argument("--status", action="store_true", help="Print current upload statistics")
    parser.add_argument("--run-next", action="store_true", help="Run the pipeline for the next sequential episode")
    parser.add_argument("--mode", choices=["full", "short", "both"], default=CONTENT_MODE, help="Processing mode")
    parser.add_argument("--dry-run", action="store_true", help="Simulate AI & video processing without uploading to YouTube")
    parser.add_argument("--privacy", choices=["unlisted", "public", "private"], default=DEFAULT_PRIVACY_STATUS)
    parser.add_argument("--target-id", type=str, default=None, help="Process a specific Google Drive file ID")

    args = parser.parse_args()

    if args.scan:
        tracker = DriveTracker()
        tracker.scan_drive()
    elif args.status:
        print_status()
    elif args.run_next:
        run_pipeline(mode=args.mode, dry_run=args.dry_run, privacy=args.privacy, target_id=args.target_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
