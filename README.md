
🎬 **Perceptual Video Quality Analysis**


This project provides a complete pipeline for encoding videos with multiple codecs, 
computing perceptual video quality metrics (**VMAF**, **PSNR**, **SSIM**), 
and plotting the results to analyze codec efficiency.

The pipeline supports **H.264**, **HEVC (H.265)**, and **AV1** codecs 
and is designed for batch processing multiple clips.


------------------------------------------------------------
⚙️ **Requirements**
------------------------------------------------------------

- **Python 3.9+**
- **FFmpeg** with **libvmaf** support
- **Python packages:** pandas, matplotlib

Install Python packages via:

    pip install pandas matplotlib

Ensure FFmpeg is installed and available in your system **PATH**.

------------------------------------------------------------
🚀 **Usage**
------------------------------------------------------------

1. Place your source clips in the **Clips/** folder.  
2. Configure bitrates and codec parameters in **Scripts/encode_clips.py** if needed.  
3. Run the full pipeline:

    python run_all.py

This will:
- Encode clips in **H.264**, **HEVC**, and **AV1** at multiple bitrates.  
- Compute **VMAF**, **PSNR**, and **SSIM** metrics.  
- Generate plots in **plots/** showing *VMAF vs Bitrate* for each clip.

------------------------------------------------------------
📊 **Output**
------------------------------------------------------------

- **Metrics:** Stored in `metrics/summary.csv` and JSON files per clip per codec.  
- **Plots:** Stored in `plots/`, e.g., `clipname_vmaf.png`.  
- **Insights:** The plots show codec efficiency — higher **VMAF** at lower bitrates indicates better compression efficiency.

------------------------------------------------------------
💡 **Example Findings**
------------------------------------------------------------

_For the `quadbike_4k` clip:_

| Codec | Bitrate | VMAF | PSNR | SSIM |
|-------|----------|------|------|------|
| **AV1**  | 1–4M | 79–96 | 42–46 | 0.97–0.99 |
| **HEVC** | 1–4M | 73–96 | 41–46 | 0.97–0.99 |
| **H.264**| 1–4M | 36–91 | 35–44 | 0.92–0.97 |

**Conclusion:**  
AV1 and HEVC deliver similar visual quality as H.264 at roughly half the bitrate, 
demonstrating superior compression efficiency.

------------------------------------------------------------
⚠️ **Notes**
------------------------------------------------------------

- Make sure `summary.csv` is closed before running `run_all.py`.  
- Large clips may take time to encode and compute metrics.  
- Scaling to 1080p is used for VMAF to speed up computation; 
  adjust in `compute_vmaf.py` if needed.

------------------------------------------------------------
📌 **License**
------------------------------------------------------------

This project is **open-source**.  
Use freely with proper attribution.
============================================================
