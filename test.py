import sounddevice as sd
import pyaudio
import numpy as np
import wave

def play_audio(file_path, virtual_device):
    # Read audio file
    with wave.open(file_path, 'rb') as wf:
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int32)
        samplerate = wf.getframerate()
    
    # Play through virtual cable
    sd.play(data, samplerate=samplerate, device=virtual_device)
    sd.wait()

play_audio("sounds/little-britain-usa-computer-sagt-nein-mp3cut.wav", 8)