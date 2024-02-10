import librosa

def get_audio_metadata(file_path):
    audio, sr = librosa.load(file_path, sr=None)
    
    metadata = {
        'sample_rate': sr,
        'duration': librosa.get_duration(y=audio, sr=sr),
        'number_of_samples': len(audio),
    }
    return metadata


file_path = r'C:\Users\Joel\Desktop\PYTHON\BCI_for_wheelchair_automation\odd\eeg_signal_LEFT_8.wav'
metadata = get_audio_metadata(file_path)

print(f"Sample Width: {metadata['sample_rate']} bytes")
print(f"Channels: {metadata['number_of_samples']}")
print(f"Duration: {metadata['duration']} seconds")
