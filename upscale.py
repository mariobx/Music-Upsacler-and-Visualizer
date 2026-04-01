import argparse
import os
import subprocess
import sys
import shutil
import numpy as np
import soundfile as sf
import torch
from pedalboard import Pedalboard, Compressor, HighpassFilter
from pedalboard.io import AudioFile

def run_cmd(cmd, step_name):
    print(f"[*] Running {step_name}...")
    binary = cmd.split()[0]
    if subprocess.run(f"command -v {binary}", shell=True, capture_output=True).returncode != 0:
        print(f"[!] Warning: {binary} not found in PATH. Skipping {step_name}.")
        return False
    try:
        subprocess.run(cmd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during {step_name}. Exit code: {e.returncode}")
        return False

def main():
    # Threading validation
    cpu_count = os.cpu_count() or 1
    parser = argparse.ArgumentParser(description="Upscale audio using Demucs, DeepFilterNet, AudioSR, and Pedalboard.")
    parser.add_argument("input", help="Path to the input audio file.")
    parser.add_argument("output", help="Path to the output upscaled audio file.")
    parser.add_argument(
        "-t", "--threads", 
        type=int, 
        default=cpu_count, 
        help=f"Number of threads to use (max: {cpu_count})."
    )
    parser.add_argument(
        "--keep-temp", 
        action="store_true", 
        help="Do not delete the temporary upscale_temp directory."
    )
    args = parser.parse_args()

    # Threading validation
    cpu_count = os.cpu_count() or 1
    if args.threads > cpu_count:
        print(f"[!] Warning: Requested {args.threads} threads but only {cpu_count} available. Capping to {cpu_count}.")
        args.threads = cpu_count
    
    if args.threads > 0:
        print(f"[*] Setting thread limit to {args.threads}")
        torch.set_num_threads(args.threads)

    input_file = os.path.abspath(args.input)
    output_file = os.path.abspath(args.output)

    if not os.path.exists(input_file):
        print(f"Error: Input file does not exist: {input_file}")
        sys.exit(1)

    out_dir = os.path.dirname(output_file)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)

    work_dir = os.path.join(out_dir, "upscale_temp")
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Path to venv binaries
    venv_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin")
    demucs_cmd = os.path.join(venv_bin, "demucs")
    deepfilter_cmd = os.path.join(venv_bin, "deepFilter")
    audiosr_cmd = os.path.join(venv_bin, "audiosr")

    # 1. Demucs separation
    jobs_flag = f"-j {args.threads}" if args.threads > 0 else ""
    run_cmd(f"{demucs_cmd} {jobs_flag} -n htdemucs -o \"{work_dir}\" \"{input_file}\"", "Demucs (Separation)")

    # Demucs puts files in work_dir/htdemucs/base_name/
    demucs_out = os.path.join(work_dir, "htdemucs", base_name)
    vocals_wav = os.path.join(demucs_out, "vocals.wav")
    drums_wav = os.path.join(demucs_out, "drums.wav")
    bass_wav = os.path.join(demucs_out, "bass.wav")
    other_wav = os.path.join(demucs_out, "other.wav")

    # 2. DeepFilterNet denoising on vocals
    run_cmd(f"{deepfilter_cmd} \"{vocals_wav}\" -o \"{demucs_out}\"", "DeepFilterNet (Vocals Denoising)")
    clean_vocals_wav = os.path.join(demucs_out, "vocals_DeepFilterNet.wav")

    stems_to_sr = {
        "vocals": clean_vocals_wav if os.path.exists(clean_vocals_wav) else vocals_wav,
        "drums": drums_wav,
        "bass": bass_wav,
        "other": other_wav
    }

    # 3. AudioSR Bandwidth Extension
    sr_stems_paths = []
    sr_input_list = os.path.join(work_dir, "sr_inputs.txt")
    
    with open(sr_input_list, "w") as f:
        for name, path in stems_to_sr.items():
            if os.path.exists(path):
                f.write(f"{path}\n")

    print("[*] Running AudioSR Batch (This will take 4x as long as one stem)...")
    if run_cmd(f"{audiosr_cmd} -il \"{sr_input_list}\" -s \"{work_dir}\"", "AudioSR Batch"):
        # Find all generated SR files
        for name, path in stems_to_sr.items():
            base_stem = os.path.splitext(os.path.basename(path))[0]
            matches = [f for f in os.listdir(work_dir) if f.startswith(base_stem) and f.endswith(".wav") and f != base_stem + ".wav"]
            if matches:
                sr_file = max([os.path.join(work_dir, m) for m in matches], key=os.path.getmtime)
                sr_stems_paths.append(sr_file)
            else:
                sr_stems_paths.append(path)
    else:
        # Fallback if AudioSR fails
        sr_stems_paths = list(stems_to_sr.values())

    # 4. Mixing and Stereo Widening
    print("[*] Mixing stems and applying Mid-Side EQ / Mastering...")
    mix = None
    sr = 48000
    for stem_path in sr_stems_paths:
        if not os.path.exists(stem_path):
            continue
        audio, rate = sf.read(stem_path)
        sr = rate
        if mix is None:
            mix = audio
        else:
            min_len = min(len(mix), len(audio))
            if len(mix.shape) > 1:
                mix = mix[:min_len, :] + audio[:min_len, :]
            else:
                mix = mix[:min_len] + audio[:min_len]

    if mix is None:
        print("Error: No stems processed.")
        sys.exit(1)

    # Convert to Stereo if Mono
    if len(mix.shape) == 1:
        mix = np.column_stack((mix, mix))
    elif mix.shape[1] == 1:
        mix = np.column_stack((mix[:, 0], mix[:, 0]))

    # Mid-Side Widening
    left = mix[:, 0]
    right = mix[:, 1]
    mid = (left + right) / 2.0
    side = (left - right) / 2.0

    # Boost side by 30% for wider orchestra
    side = side * 1.3

    mix[:, 0] = mid + side
    mix[:, 1] = mid - side

    # Normalize to prevent clipping
    max_val = np.max(np.abs(mix))
    if max_val > 0.95:
        mix = mix / max_val * 0.95

    temp_mix_path = os.path.join(work_dir, "temp_mix.wav")
    sf.write(temp_mix_path, mix, sr)

    # Pedalboard Mastering
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=30),
        Compressor(threshold_db=-14, ratio=2.5, attack_ms=10.0, release_ms=100.0)
    ])

    with AudioFile(temp_mix_path) as f:
        with AudioFile(output_file, 'w', f.samplerate, f.num_channels) as o:
            while f.tell() < f.frames:
                chunk = f.read(f.samplerate)
                effected = board(chunk, f.samplerate, reset=False)
                o.write(effected)

    if not args.keep_temp:
        print(f"[*] Cleaning up temporary files in {work_dir}...")
        shutil.rmtree(work_dir)

    print(f"[*] Upscaling complete! Output saved to: {output_file}")

if __name__ == "__main__":
    main()
