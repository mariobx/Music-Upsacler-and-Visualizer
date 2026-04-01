import argparse
import os
import subprocess
import sys
import re

def sanitize_title(title):
    # Remove characters that are problematic for filesystems
    return re.sub(r'[^\w\s\-\(\)｜@]', '', title).strip().replace(' ', '_')

def get_video_title(url, venv_python):
    print(f"[*] Fetching video title from YouTube...")
    try:
        # Use yt-dlp to get the title
        cmd = [os.path.join(os.path.dirname(venv_python), "yt-dlp"), "--get-filename", "-o", "%(title)s", url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error fetching title: {e}")
        return "downloaded_video"

def main():
    # Default paths for processing
    cwd = os.getcwd()
    default_to_upscale = os.path.join(cwd, "to_upscale")
    default_post_upscaled = os.path.join(cwd, "post_upscaled")
    default_final_video = os.path.join(cwd, "final_video")

    # Threading validation
    cpu_count = os.cpu_count() or 1
    parser = argparse.ArgumentParser(description="Master script for YouTube download, upscaling, and comparison video generation.")
    parser.add_argument("url", help="The YouTube URL to process.")
    parser.add_argument("-f", "--format", default="mp3", help="The audio format to download (default: mp3).")
    parser.add_argument("-t", "--threads", type=int, default=cpu_count, help=f"Number of threads for upscaling (max: {cpu_count}).")
    parser.add_argument("--to_upscale", default=default_to_upscale, help=f"Base directory for downloads (default: {default_to_upscale})")
    parser.add_argument("--post_upscaled", default=default_post_upscaled, help=f"Base directory for upscaled files (default: {default_post_upscaled})")
    parser.add_argument("--final_video_dir", default=default_final_video, help=f"Base directory for final comparison (default: {default_final_video})")
    
    args = parser.parse_args()

    # Paths to internal scripts and venv
    root_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(root_dir, "venv/bin/python3")
    yt_grab_script = os.path.join(root_dir, "yt_grab.py")
    musialize_script = os.path.join(root_dir, "musialize.py")
    upscale_script = os.path.join(root_dir, "upscale.py")

    # 1. Get Title and Sanitize
    raw_title = get_video_title(args.url, venv_python)
    safe_title = sanitize_title(raw_title)
    print(f"[*] Processing: {raw_title} (Safe name: {safe_title})")

    # 2. Setup "To Upscale" directory structure
    to_upscale_dir = os.path.join(args.to_upscale, safe_title)
    to_audio_dir = os.path.join(to_upscale_dir, "audio")
    to_visual_dir = os.path.join(to_upscale_dir, "visual")
    os.makedirs(to_audio_dir, exist_ok=True)
    os.makedirs(to_visual_dir, exist_ok=True)

    # 3. Download Audio
    print("[*] Step 2: Downloading audio...")
    subprocess.run([venv_python, yt_grab_script, args.url, "-f", args.format, "-o", to_audio_dir], check=True)
    
    # Find the downloaded file (it might have spaces or weird characters if yt-dlp was literal)
    downloaded_files = [f for f in os.listdir(to_audio_dir) if f.endswith(args.format)]
    if not downloaded_files:
        print("Error: Could not find downloaded audio file.")
        return
    original_audio_path = os.path.join(to_audio_dir, downloaded_files[0])

    # 4. Create "Before" Visualizer
    print("[*] Step 3: Generating 'Before' visualizer...")
    before_video_path = os.path.join(to_visual_dir, f"{safe_title}.mp4")
    subprocess.run([venv_python, musialize_script, original_audio_path, before_video_path], check=True)

    # 5. Setup "Post Upscaled" directory structure
    post_upscale_dir = os.path.join(args.post_upscaled, safe_title)
    post_audio_dir = os.path.join(post_upscale_dir, "audio")
    post_visual_dir = os.path.join(post_upscale_dir, "visual")
    os.makedirs(post_audio_dir, exist_ok=True)
    os.makedirs(post_visual_dir, exist_ok=True)

    # 6. Upscale Audio
    print("[*] Step 5: Upscaling audio (this will take a while)...")
    upscaled_audio_path = os.path.join(post_audio_dir, f"{safe_title}_upscaled.wav")
    subprocess.run([venv_python, upscale_script, original_audio_path, upscaled_audio_path, "-t", str(args.threads)], check=True)

    # 7. Create "After" Visualizer
    print("[*] Step 6: Generating 'After' visualizer...")
    after_video_path = os.path.join(post_visual_dir, f"{safe_title}_upscaled.mp4")
    subprocess.run([venv_python, musialize_script, upscaled_audio_path, after_video_path], check=True)

    # 8. Setup "Final Video" directory
    final_video_out_dir = os.path.join(args.final_video_dir, safe_title)
    os.makedirs(final_video_out_dir, exist_ok=True)
    final_output_path = os.path.join(final_video_out_dir, f"{safe_title}_comparison.mp4")

    # 9. FFmpeg Side-by-Side Stitch
    print("[*] Step 9: Stitching comparison video with FFmpeg...")
    # Complex filter for: Side-by-Side, Black Border (10px), and "BEFORE/AFTER" labels
    filter_complex = (
        f"[0:v]pad=iw*2+10:ih:color=black[bg]; "
        f"[bg][1:v]overlay=W/2+5:0[vid]; "
        f"[vid]drawtext=text='BEFORE':fontcolor=white:fontsize=60:x=(w/4-text_w/2):y=40:bordercolor=black:borderw=3,"
        f"drawtext=text='AFTER':fontcolor=white:fontsize=60:x=(3*w/4-text_w/2):y=40:bordercolor=black:borderw=3[outv]"
    )

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", before_video_path,
        "-i", after_video_path,
        "-i", upscaled_audio_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "2:a",
        "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "256k",
        final_output_path
    ]

    # 10. Create Description File
    print("[*] Step 10: Creating description file...")
    description_path = os.path.join(final_video_out_dir, "description.txt")
    tools_used = "Demucs (Separation), DeepFilterNet (Denoising), AudioSR (Super-Resolution), Pedalboard (Mastering), and Musializer (Visualization)"
    description_content = (
        f"This comparison video was created using {tools_used}.\n"
        f"The original audio came from {args.url}.\n"
        f"Created by https://github.com/mariobx\n"
    )
    with open(description_path, "w") as desc_file:
        description_file_content = description_content
        desc_file.write(description_file_content)

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"\n[!] MISSION ACCOMPLISHED.")
        print(f"[!] Original Audio: {original_audio_path}")
        print(f"[!] Upscaled Audio: {upscaled_audio_path}")
        print(f"[!] Final Comparison: {final_output_path}")
        print(f"[!] Description: {description_path}")
    except Exception as e:
        print(f"Error during FFmpeg stitching: {e}")

if __name__ == "__main__":
    main()
