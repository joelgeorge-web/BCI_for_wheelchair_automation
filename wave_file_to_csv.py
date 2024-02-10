import sys
import os
from scipy.io import wavfile
import pandas as pd

# Specify the folder containing WAV files
input_folder = r'C:\Users\Joel\OneDrive\Documents\BYB'

# Create an "output" folder if it doesn't exist
output_folder = 'output_06-02-2024'
os.makedirs(output_folder, exist_ok=True)

# Process all WAV files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".wav"):
        input_filepath = os.path.join(input_folder, filename)

        # Read WAV file
        sample_rate, data = wavfile.read(input_filepath)
        print(f'Loaded {filename}\n')

        # Convert to DataFrame
        wav_data = pd.DataFrame(data)
        print(f'Multi-channel WAV file\n')
        print(f'Number of channels: {len(wav_data.columns)}')

        # Save CSV file in the "output" folder with the same name as the WAV file
        output_filepath = os.path.join(output_folder, f"{filename[:-4]}.csv")
        wav_data.to_csv(output_filepath, mode='w', index=False)
        print(f'Saved {filename[:-4]}\n')

print('Conversion of all WAV files to CSV is complete.')
