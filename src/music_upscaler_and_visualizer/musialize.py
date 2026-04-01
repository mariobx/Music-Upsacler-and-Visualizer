import argparse
import os
import subprocess
import sys
try:
    from git import Repo
except ImportError:
    Repo = None

def run_musializer(input_path, output_path, musializer_dir=None):
    if musializer_dir is None:
        # Default to current working directory or a common location
        musializer_dir = os.path.join(os.getcwd(), "musializer-file-paths")

    musializer_path = os.path.join(musializer_dir, "build", "musializer")

    if not os.path.exists(musializer_dir):
        print(f"[*] Musializer directory not found at {musializer_dir}. Cloning from GitHub...")
        if Repo is None:
            print("Error: GitPython is not installed. Please install it with 'pip install GitPython'.")
            return False
        try:
            Repo.clone_from("https://github.com/mariobx/musializer-file-paths", musializer_dir)
        except Exception as e:
            print(f"Error: Failed to clone musializer-file-paths repository: {e}")
            return False

    if not os.path.exists(musializer_path):
        print(f"Error: Musializer executable not found at {musializer_path}")
        print(f"Please compile the C project in {musializer_dir}")
        print("Steps: cd musializer-file-paths && cc -o nob nob.c && ./nob")
        return False

    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        return False

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Running musializer: {input_path} -> {output_path}")
    
    try:
        # Run the tool
        subprocess.run([musializer_path, input_path, output_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Musializer failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Wrap the musializer tool for easier use.")
    parser.add_argument("input", help="Path to the input audio file.")
    parser.add_argument("output", help="Path to the output video file.")
    parser.add_argument("--musializer_dir", help="Path to the musializer-file-paths directory.")
    
    args = parser.parse_args()
    run_musializer(args.input, args.output, args.musializer_dir)

if __name__ == "__main__":
    main()
