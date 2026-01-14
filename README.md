# Pathogen Detection

This repository contains the **Pathogen Detection** software developed as part of the **UM-Dearborn Pathogen Database** project. The tool processes ion mobility data to perform preprocessing, calibration, quality control, and feature extraction for downstream pathogen analysis.

---

## 📦 Installation

1. Download and unzip `PathogenDetection.zip`
2. Ensure all required files and directories are present:

├── init.py
├── BaselineCorrection.py
├── config.yaml
├── Data/
├── FeatureMatrix.py
├── Global.py
├── Helper.py
├── IntensityCalibration.py
├── Launch_MacOS.sh
├── Launch_Windows.bat
├── metadata.csv
├── Pathogen.py
├── PeakBinning.py
├── PeakDetection.py
├── Preprocessing.py
├── QualityControl.py
└── README.md

yaml
Copy code

---

## ✅ Before Starting

1. Place all **ion mobility data files** in the `Data/` directory.
2. Replace `metadata.csv` with a CSV file corresponding to the data stored in `Data/`.
3. Ensure **Python 3.11 or higher** is installed:
   ```bash
   python3 --version
▶️ Startup
Launching the Program
Windows
Double-click:

Copy code
Launch_Windows.bat
macOS
Work in progress.
Currently supported via Windows emulation (e.g., VMware Fusion).

📥 First Run Behavior
Required Python packages will automatically download on first launch.

Ensure you are connected to the internet.

After the first run, you may edit values in config.yaml if needed.

⚙️ Configuration Notes
Only modify values in config.yaml if you understand their purpose.

If using a remote database host, update the database connection values.

The num-components parameter:

Must be less than the number of samples

If set higher, it will automatically default to:

typescript
Copy code
number of samples - 1
📁 Data Requirements
A minimum of two samples is required to run the program.

All samples must be correctly referenced in metadata.csv.

🧪 Modules Overview
Preprocessing – Initial data cleaning and normalization

BaselineCorrection – Signal baseline adjustment

IntensityCalibration – Calibration of signal intensities

PeakDetection – Identification of significant peaks

PeakBinning – Grouping of peaks across samples

FeatureMatrix – Feature extraction and matrix generation

QualityControl – Validation and QC checks

📝 Notes
Ensure the Data/ directory and metadata file are consistent.

Misconfigured parameters may lead to invalid results.

This software is intended for research and educational use.

📫 Support
For issues, questions, or improvements, please open a GitHub issue in this repository.

🙏 Acknowledgments
Developed under the UM-Dearborn Pathogen Database initiative.
