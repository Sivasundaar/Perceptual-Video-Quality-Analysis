import pandas as pd
import matplotlib.pyplot as plt
import os
import re

# --- Configuration and Setup ---
# Read the combined results CSV into a pandas DataFrame
df = pd.read_csv("metrics/summary.csv")

# Create the output directory for the plots if it doesn't exist
os.makedirs("plots", exist_ok=True)

# --- Identify Unique Clips ---
# Extract unique base clip names (e.g., 'football_4k', 'quadbike_4k')
# by splitting the full clip name and ignoring the last segment (which is the bitrate).
base_names = sorted({"_".join(c.split("_")[:-1]) for c in df["Clip"]})

# --- Main Plotting Loop ---
# Loop through each unique base clip name to generate a separate plot
for clip_base in base_names:
    # Initialize a new figure for the current clip
    plt.figure(figsize=(6, 4))
    
    # Loop through each unique codec (AV1, H264, HEVC)
    for codec in df["Codec"].unique():
        # Get all rows for the current codec
        subset = df[df["Codec"] == codec]
        
        # Get the rows specific to the current base clip (e.g., all 'football_4k' encodes)
        rows = subset[subset["Clip"].str.startswith(clip_base)]
        if rows.empty:
            continue

        # --- Bitrate Parsing (X-Axis Data) ---
        # Extract the bitrate number from the end of the filename (e.g., 'football_4k_1M.mp4' -> 1)
        # This is a robust way to handle the naming convention.
        bitrates = []
        for clip_name in rows["Clip"]:
            # Safely extract the bitrate (e.g., '1M.mp4' or '2M.mp4')
            bitrate_str_suffix = clip_name.split("_")[-1]
            # Remove 'M.mp4' and parse as an integer (e.g., "1" -> 1)
            try:
                # Use regex to find the number followed by 'M' or just the number
                match = re.search(r"(\d+)M?\.mp4", bitrate_str_suffix)
                if match:
                    bitrates.append(int(match.group(1)))
                else:
                    # Fallback for filenames without 'M' if necessary
                    bitrates.append(int(bitrate_str_suffix.replace(".mp4", "")))
            except ValueError:
                # Handle cases where parsing fails, e.g., if the suffix is not a valid bitrate
                print(f"Warning: Could not parse bitrate from {clip_name}")
                continue
        
        # --- Plotting the Rate-Quality Curve ---
        # Plot VMAF Score (Y) against Bitrate (X)
        plt.plot(bitrates, rows["VMAF"], marker="o", label=codec.upper())

    # --- Plot Customization ---
    plt.title(f"VMAF vs Bitrate - {clip_base}")
    plt.xlabel("Bitrate (Mbps)")
    plt.ylabel("VMAF Score")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the figure to the plots directory
    plt.savefig(f"plots/{clip_base}_vmaf.png")
    # Close the figure to free up memory before the next loop iteration
    plt.close()

print("✅ Plots saved in 'plots/'")