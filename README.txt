README

On installation:
	1. Unzip PathogenDetection.zip
	2. Ensure all files and directories are present:
		__init__.py
		BaselineCorrection.py
		config.yaml
		Data/
		FeatureMatrix.py
		Global.py
		Helper.py
		IntensityCalibration.py
		Launch_MacOS.sh
		Launch_Windows.bat
		metadata.csv
		Pathogen.py
		PeakBinning.py
		PeakDetection.py
		Preprocessing.py
		QualityControl.py
		README.md (this document)

Before Starting:
	1. Place all ion mobility data in the Data/ directory
	2. Ensure that you have replaced metadata.csv with csv file related to the data stored in the Data/
		directory
	3. Ensure that you have python3 installed by opening your command prompt or terminal and typing
		'python3 --version' and make sure that your Python version is 3.11+

Startup:
	1. Launching the program:
		MacOS: double click on 'Launch_MacOS.sh'
		Windows: double click on 'Launch_Windows.bat'
	2. Allow for packages to download, ensuring you are connected to the internet
	3. Edit config values after first run

Notes:
	- Make sure that there are more than one sample when running the program
	- Edit the database values if using a remote host
	- Only mess with the values in the config if you understand what they do
	- If num-components is set to a value higher than the sample size, num-components will default to
		sample size - 1