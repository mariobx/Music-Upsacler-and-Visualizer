# 🎶 AI Music Upscaling & Visualization Pipeline

A professional-grade automated pipeline to transform low-fidelity historical recordings (or any YouTube audio) into modern, high-bandwidth stereo masters with cinematic visualizations.

## 🛠 Features
- **Automated Workflow:** From YouTube URL to side-by-side comparison video in one command.
- **Deep Learning Separation:** Uses **Demucs (htdemucs)** to isolate vocals from instrumentation.
- **Vocal Denoising:** Uses **DeepFilterNet** to remove background hiss without artifacts.
- **Bandwidth Extension:** Uses **AudioSR (Latent Diffusion)** to "hallucinate" missing high frequencies (up to 48kHz).
- **Mastering & Widening:** Mid-Side EQ widening and compression via Spotify's **Pedalboard**.
- **Cinematic Visuals:** Dual-window visualization powered by a custom fork of **Tsoding's Musializer**.

## 🏗 The Pipeline
1. **Fetch:** Downloads audio via `yt-dlp`.
2. **Visualize (Before):** Generates a 1920x1080 visualizer of the raw audio.
3. **Separate:** Un-mixes the track into Vocals, Drums, Bass, and Other.
4. **Denoise:** Cleans the vocal stem using DeepFilterNet.
5. **Upscale:** Applies Super-Resolution diffusion to all four stems.
6. **Master:** Re-mixes, widens the stereo image by 30%, and masters the final `.wav`.
7. **Visualize (After):** Generates a visualizer of the upscaled audio.
8. **Stitch:** Creates a side-by-side comparison video with "BEFORE" and "AFTER" labels using `ffmpeg`.

## 🚀 Usage

### Prerequisites
- Python 3.10 (Recommended for AI model compatibility)
- FFmpeg (Installed and in PATH)
- Rust/Cargo (For DeepFilterNet compilation)

### Installation
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Ensure musializer is built in ../musializer-fork/
```

### Running the Master Pipeline
```bash
./venv/bin/python3 main.py "YOUR_YOUTUBE_URL" -t 28
```
- `-t 28`: Uses 28 threads (optimized for Ryzen AI Max 395).
- `-f mp3`: Choose download format (default: mp3).

## 📂 Directory Structure
- `to_upscale/`: Raw downloads and "Before" visuals.
- `post_upscaled/`: Processed stems and high-fidelity "After" visuals.
- `final_video/`: The final side-by-side comparison `.mp4` and `description.txt`.

## 🙏 Credits
- **[Musializer](https://github.com/tsoding/musializer):** Original visualization engine by Tsoding.
- **[Demucs](https://github.com/facebookresearch/demucs):** Audio source separation by Meta Research.
- **[DeepFilterNet](https://github.com/Rikorose/DeepFilterNet):** Denoising by H. Schröter.
- **[AudioSR](https://github.com/haoheliu/AudioSR):** Super-resolution by Haohe Liu et al.
- **[Pedalboard](https://github.com/spotify/pedalboard):** Audio effects by Spotify.

## 📺 Hall of Fame (Uploaded Results)
*Paste your comparison video links below!*
- [Noor Jahan - Dil Jala Na Dilwaale (AI Upscaled)](https://www.youtube.com/watch?v=...)

---
Created by [mariobx](https://github.com/mariobx)
