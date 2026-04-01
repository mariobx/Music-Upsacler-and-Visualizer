# Music Upscaling & Visualization

An automated pipeline that downloads audio from YouTube, upscales it using Demucs, DeepFilterNet, and AudioSR, and generates side-by-side comparison visualizations.

## Prerequisites

- **FFmpeg**: Must be installed and available in your `PATH`.
- **C Compiler**: `cc` (Linux) or `cl.exe` (Windows/MSVC) for building the visualizer.
- **Python 3.11**: **Required.** This project relies on specific versions of `torchaudio` and `DeepFilterNet` that have compatibility issues with Python 3.12+.
- **X11 Libraries**: (Linux only) Required for building the visualizer (Musializer).
  - On Debian/Ubuntu: `sudo apt install libx11-dev libxcursor-dev libxrandr-dev libxinerama-dev libxi-dev`

## Installation

```bash
pip install Music-Upsacler-and-Visualizer
```

*Note: It is highly recommended to use a virtual environment with Python 3.11.*

## Setup

The visualization component (Musializer) needs to be compiled locally.

1. The tool will automatically clone the musializer repository if it's not present when you run it, or you can do it manually:
   ```bash
   git clone https://github.com/mariobx/musializer-file-paths
   ```

2. Compile the binary:
   - **Linux**: `cd musializer-file-paths && cc -o nob nob.c && ./nob`
   - **Windows (MSVC)**: `cd musializer-file-paths && cl.exe nob.c && nob.exe`

The tool expects the binary at `./musializer-file-paths/build/musializer` by default, or you can specify the path using `--musializer_dir`.

## Usage

After installation, you can use the `musicupscaler` command:

```bash
musicupscaler <YOUTUBE_URL>
```

### Options:
- `-f`, `--format`: Audio format to download (`mp3`, `m4a`, `wav`, `flac`) (default: `mp3`).
- `-t`, `--threads`: Number of threads for upscaling.
- `--to_upscale`: Directory for initial downloads.
- `--post_upscaled`: Directory for upscaled audio.
- `--final_video_dir`: Directory for the final comparison video.
- `--musializer_dir`: Path to the compiled Musializer directory.

## How it Works

1. **Download**: Uses `yt-dlp` to fetch the highest quality audio.
2. **Upscale**:
   - **Demucs**: Separates audio into stems.
   - **DeepFilterNet**: Denoises the vocal stem.
   - **AudioSR**: Performs Super-Resolution (48kHz).
   - **Pedalboard**: Mixes, masters, and applies stereo widening.
3. **Visualize**: Uses a custom build of Musializer to generate waveforms.
4. **Stitch**: FFmpeg creates a side-by-side "BEFORE" vs "AFTER" comparison video.

---
Created by [mariobx](https://github.com/mariobx)
