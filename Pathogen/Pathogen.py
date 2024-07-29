def main():
    print("Hello Pathogen Project!")

if __name__ == "__main__":
    main()

# 1. Move Import
# Open the file in read mode
with open('Pathogen/TestData/air.POSITIVE.txt', 'r') as file:
    # Read the contents of the file
    contents = file.read()

# Print the contents
print(contents)

#2. Quality Control

#3. Transormational Smoothing

#4. Baseline Correction

#5. Intensity Calibration

#6. Spectra Alignment

#7. Peak Detection

#8. Peak Binning

#9. Feature Matrix