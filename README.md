# Music Upscaling & Visualization Pipeline

This project is an automated pipeline that downloads audio from YouTube, upscales it using advanced AI models (Demucs, DeepFilterNet, AudioSR), and generates side-by-side comparison visualizations using a custom build of Musializer.

## Prerequisites

- **FFmpeg**: Must be installed and available in your `PATH`.
- **C Compiler**: `cc` (Linux) or `cl.exe` (Windows/MSVC) for building the visualizer.
- **Python 3.11**: **Required.** This project relies on specific versions of `torchaudio` and `DeepFilterNet` that have compatibility issues with Python 3.12+.
- **X11 Libraries**: (Linux only) Required for building and running the visualizer (Musializer).
  - On Debian/Ubuntu: `sudo apt install libx11-dev libxcursor-dev libxrandr-dev libxinerama-dev libxi-dev`
  - On Arch: `sudo pacman -S libx11 libxcursor libxrandr libxinerama libxi`

## Step 1: Compile the Musializer (C Project)

The visualization component is a fork of Musializer created by youtuber Tsoding located in the `mariobx/musializer-file-paths` directory. You must compile it before running the Python scripts. 

1. Navigate to the musializer directory:
   ```bash
   cd musializer-file-paths
   ```

2. Bootstrap the `nob` build system:
   - **Linux**: `cc -o nob nob.c && ./nob`
   - **Windows (MSVC)**: `cl.exe nob.c && nob.exe`

This will create a `build/` directory containing the `musializer` executable. The Python scripts expect this binary to be at `musializer-file-paths/build/musializer`.

## Step 2: Setup the Python Environment

1. Create a virtual environment using **Python 3.11**:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

2. Install the required dependencies:
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```
   *Note: `torchaudio` is pinned to version 2.1.2 in `requirements.txt` to maintain compatibility with `DeepFilterNet`. If you encounter import errors, ensure you are using Python 3.11.*

## Step 3: Run the Pipeline

The `main.py` script handles the entire process: downloading, upscaling, and generating the comparison video.

```bash
python main.py <YOUTUBE_URL>
```

### Options:
- `-f`, `--format`: Audio format to download (`mp3`, `m4a`, `wav`, `flac`) (default: `mp3`).
- `-t`, `--threads`: Number of threads for upscaling (max: dependent on your system).
- `--to_upscale`: Directory for initial downloads.
- `--post_upscaled`: Directory for upscaled audio.
- `--final_video_dir`: Directory for the final comparison video.

## How it Works

1. **`yt_grab.py`**: Downloads the highest quality audio from the provided YouTube URL.
2. **`musialize.py`**: A wrapper for the compiled `musializer` binary. It generates a video visualization of the audio.
3. **`upscale.py`**: The core upscaling engine:
   - **Demucs**: Separates the audio into stems (vocals, drums, bass, other).
   - **DeepFilterNet**: Denoises the vocal stem.
   - **AudioSR**: Performs Super-Resolution to restore high-frequency components.
   - **Pedalboard**: Mixes and masters the upscaled stems.
4. **`main.py`**: Orchestrates the steps above and uses FFmpeg to create a side-by-side comparison video with "BEFORE" and "AFTER" labels.

---
