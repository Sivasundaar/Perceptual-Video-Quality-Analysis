import subprocess
import os

# --- Setup: Create Necessary Directories ---
# Ensure 'metrics' and 'plots' directories exist before the scripts try to write to them.
os.makedirs("metrics", exist_ok=True)
os.makedirs("plots", exist_ok=True)

# --- Step 1: Encode Videos ---
print("➡️ Encoding clips ...")
# Execute the encoding script. 'check=True' ensures the script stops if encoding fails.
subprocess.run(["python", "Scripts/encode_clips.py"], check=True)

# --- Step 2: Compute Quality Metrics ---
print("➡️ Computing VMAF metrics ...")
# Execute the VMAF, PSNR, and SSIM calculation script.
subprocess.run(["python", "Scripts/compute_vmaf.py"], check=True)

# --- Step 3: Plot Results ---
print("➡️ Plotting results ...")
# Execute the plotting script to generate the final Rate-Quality charts.
subprocess.run(["python", "Scripts/plot_results.py"], check=True)

# --- Completion Message ---
print("✅ All done! Check 'plots/' for VMAF charts.")