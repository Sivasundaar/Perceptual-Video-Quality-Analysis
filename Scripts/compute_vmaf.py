import os
import json
import subprocess
import csv
import time
import re

# --- Configuration ---
# Define directory paths for source, encoded, and metric files
SOURCE_DIR = "Clips"
ENCODED_DIR = "encoded_clips"
METRICS_DIR = "metrics"

# Create the directory for saving metrics if it doesn't exist
os.makedirs(METRICS_DIR, exist_ok=True)
# Define the path for the final summary CSV file
summary_csv = os.path.join(METRICS_DIR, "summary.csv")

# --- Initialization and Setup ---
# Clean up the previous summary file to start fresh
if os.path.exists(summary_csv):
    try:
        os.remove(summary_csv)
    except PermissionError:
        # Crucial check: prevents error if the user has the file open
        print("⚠️ Close summary.csv if open in Excel, then re-run.")
        exit(1)

# List to store the results of all clips
results = []

# --- Main Logic: Iterate and Compute Metrics ---
# Loop through all codec subdirectories (e.g., 'av1', 'h264', 'hevc')
for codec in os.listdir(ENCODED_DIR):
    codec_dir = os.path.join(ENCODED_DIR, codec)
    if not os.path.isdir(codec_dir):
        continue

    # Loop through each encoded clip in the current codec directory
    for enc_clip in os.listdir(codec_dir):
        if not enc_clip.lower().endswith(".mp4"):
            continue

        # --- Path and Filename Extraction ---
        enc_path = os.path.join(codec_dir, enc_clip)
        
        # Determine the reference clip name (e.g., 'football_4k_1M.mp4' -> 'football_4k.mp4')
        base_name = "_".join(enc_clip.split("_")[:-1])
        ref_path = os.path.join(SOURCE_DIR, base_name + ".mp4")
        
        # Define the VMAF JSON log path, using forward slashes for FFmpeg compatibility
        # and removing the '.mp4' to add '_metrics.json'
        json_path = os.path.join(METRICS_DIR, enc_clip.replace(".mp4", "_metrics.json")).replace("\\", "/")

        # --- Pre-Check ---
        if not os.path.exists(ref_path):
            print(f"⚠️ Skipping {enc_clip}: missing reference {ref_path}")
            continue

        print(f"\n🎯 Computing VMAF for {enc_clip} using {codec.upper()} ...")

        # --- 1. VMAF Calculation (libvmaf) ---
        # The filter graph rescales both reference (0:v) and distorted (1:v) clips 
        # to a common 1080p resolution (1920x1080) for a consistent VMAF calculation.
        ffmpeg_cmd = [
            "ffmpeg", "-hide_banner",
            "-i", ref_path,
            "-i", enc_path,
            "-lavfi",
            # Rescale videos for VMAF calculation 
            f"[0:v]scale=1920:1080:flags=bicubic[ref];"
            f"[1:v]scale=1920:1080:flags=bicubic[dist];"
            # Apply VMAF filter on the rescaled streams, logging output to JSON
            f"[dist][ref]libvmaf=log_fmt=json:log_path='{json_path}'", # Path quoted for robustness
            "-f", "null", "-"
        ]

        # Run FFmpeg, suppressing output to keep the console clean
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # CRITICAL FIX: Add a small delay to ensure the OS writes the JSON file before Python reads it
        time.sleep(0.5)

        # Initialize metric variables
        vmaf = psnr = ssim = 0.0
        
        # --- VMAF Data Extraction ---
        try:
            with open(json_path) as f:
                data = json.load(f)
                # Handle possible VMAF JSON format variations ('pooled_metrics' vs 'aggregate')
                if "pooled_metrics" in data:
                    vmaf = data["pooled_metrics"]["vmaf"]["mean"]
                elif "aggregate" in data:
                    vmaf = data["aggregate"].get("vmaf", 0)
        except Exception as e:
            # Report error but continue to next clip
            print(f"❌ Could not parse VMAF JSON: {e}")

        # --- 2. PSNR Calculation ---
        psnr_cmd = [
            "ffmpeg", "-hide_banner",
            "-i", ref_path,
            "-i", enc_path,
            "-lavfi", "psnr", # PSNR filter
            "-f", "null", "-"
        ]
        # Run PSNR command, capturing stderr where the results are typically printed
        psnr_proc = subprocess.run(psnr_cmd, capture_output=True, text=True)
        # Use RegEx to search for the final 'average' value in the output
        m = re.search(r"average:([\d\.]+)", psnr_proc.stderr)
        if m:
            psnr = float(m.group(1))

        # --- 3. SSIM Calculation ---
        ssim_cmd = [
            "ffmpeg", "-hide_banner",
            "-i", ref_path,
            "-i", enc_path,
            "-lavfi", "ssim", # SSIM filter
            "-f", "null", "-"
        ]
        # Run SSIM command, capturing stderr
        ssim_proc = subprocess.run(ssim_cmd, capture_output=True, text=True)
        # Use RegEx to search for the final 'All' value in the output
        m = re.search(r"All:([\d\.]+)", ssim_proc.stderr)
        if m:
            ssim = float(m.group(1))

        # Store the collected metrics for the current clip
        results.append([enc_clip, codec, vmaf, psnr, ssim])
        print(f"✅ Done: VMAF={vmaf:.2f}, PSNR={psnr:.2f}, SSIM={ssim:.4f}")

# --- Final Output: Write CSV ---
with open(summary_csv, "w", newline="") as f:
    writer = csv.writer(f)
    # Write the header row
    writer.writerow(["Clip", "Codec", "VMAF", "PSNR", "SSIM"])
    # Write all collected results
    writer.writerows(results)

print(f"\n✅ All metrics saved to {summary_csv}")