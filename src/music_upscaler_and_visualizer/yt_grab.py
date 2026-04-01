import argparse
import os
import yt_dlp

def download_audio(url, format="mp3", output_dir="."):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Failed to download audio: {e}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Download audio from a YouTube link.")
    parser.add_argument("url", help="The YouTube video URL to download.")
    parser.add_argument(
        "-f", "--format", 
        choices=["mp3", "m4a", "wav", "flac"], 
        default="mp3", 
        help="The audio format to download (default: mp3)."
    )
    parser.add_argument(
        "-o", "--output_dir", 
        default=".", 
        help="The directory where the file will be saved (default: current directory)."
    )

    args = parser.parse_args()
    download_audio(args.url, args.format, args.output_dir)

if __name__ == "__main__":
    main()
