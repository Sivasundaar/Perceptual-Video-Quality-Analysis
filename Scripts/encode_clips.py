import os
import subprocess
import time

# --- Configuration: Codec and Encoding Parameters ---
# Defines the FFmpeg parameters specific to each codec.
# - The 'preset' controls the encoding speed/efficiency trade-off (slower = better quality/size).
# - '-rc 1' (Rate Control Mode 1) for libsvtav1 enables 1-pass VBR, equivalent to the 2-pass target.
CODEC_PARAMS = {
    "h264": ["-c:v", "libx264", "-preset", "medium"],
    "hevc": ["-c:v", "libx265", "-preset", "medium"],
    "av1":  ["-c:v", "libsvtav1", "-preset", "7", "-rc", "1"]
}

# The list of target bitrates (in bits per second) for the VMAF comparison.
BITRATES = ["1M", "2M", "4M"]

# --- Directory Setup ---
SOURCE_DIR = "Clips"
OUTPUT_DIR = "encoded_clips"
# Create the main output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Main Encoding Loop ---
# Iterate through all video files in the source directory
for clip in os.listdir(SOURCE_DIR):
    if not clip.lower().endswith(".mp4"):
        continue

    clip_path = os.path.join(SOURCE_DIR, clip)
    # Extract the base filename (e.g., 'football_4k')
    name, _ = os.path.splitext(clip)

    # Iterate through each defined codec (h264, hevc, av1)
    for codec, params in CODEC_PARAMS.items():
        codec_dir = os.path.join(OUTPUT_DIR, codec)
        # Create a subdirectory for the current codec (e.g., 'encoded_clips/av1')
        os.makedirs(codec_dir, exist_ok=True)

        # Iterate through each target bitrate (1M, 2M, 4M)
        for br in BITRATES:
            print(f"🎬 Encoding {clip} → {codec.upper()} @ {br} ...")
            # Define the final output path for the encoded clip
            out_path = os.path.join(codec_dir, f"{name}_{br}.mp4")

            # --- H264 and HEVC: Use 2-Pass VBR Encoding ---
            # 2-Pass ensures better quality by analyzing the video content in the first pass
            if codec in ["h264", "hevc"]:
                # Passlog file is used by FFmpeg to store analysis data from the first pass
                log_file = os.path.join(codec_dir, f"{name}_{br}_log")
                
                # --- PASS 1: Analysis ---
                cmd1 = [
                    "ffmpeg", "-y", "-i", clip_path, # '-y' overwrites output without asking
                    *params, "-b:v", br,
                    "-pass", "1", "-passlogfile", log_file,
                    "-f", "mp4", os.devnull # Output is discarded to /dev/null
                ]
                # Run Pass 1, suppressing output to keep console clean
                subprocess.run(cmd1, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # CRITICAL: A short delay to ensure the passlog file is completely written to disk
                time.sleep(0.3)

                # --- PASS 2: Encoding ---
                cmd2 = [
                    "ffmpeg", "-y", "-i", clip_path,
                    *params, "-b:v", br,
                    "-pass", "2", "-passlogfile", log_file,
                    out_path # Final output file
                ]
                # Run Pass 2 (this time we don't suppress the output for easier debugging of the final command)
                subprocess.run(cmd2, check=True)
                
            # --- AV1: Use 1-Pass Encoding ---
            # Modern AV1 encoders often use a high-quality 1-pass VBR or ABR mode
            # which is faster and sufficient for comparative analysis.
            else:
                cmd = ["ffmpeg", "-y", "-i", clip_path, *params, "-b:v", br, out_path]
                # Run the single pass encoding
                subprocess.run(cmd, check=True)

print("\n✅ All clips encoded successfully.")