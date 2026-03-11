import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Wrap the musializer tool for easier use.")
    parser.add_argument("input", help="Path to the input audio file.")
    parser.add_argument("output", help="Path to the output video file.")
    
    args = parser.parse_args()

    # The path to the musializer executable we found earlier
    musializer_path = os.path.abspath("../musializer-fork/musializer-file-paths/build/musializer")

    if not os.path.exists(musializer_path):
        print(f"Error: Musializer executable not found at {musializer_path}")
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"Error: Input file not found at {args.input}")
        sys.exit(1)

    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Running musializer: {args.input} -> {args.output}")
    
    try:
        # Run the tool
        subprocess.run([musializer_path, args.input, args.output], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Musializer failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
