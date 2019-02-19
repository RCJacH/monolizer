import os
import numpy as np
from soundfile import write


def transpose(samples):
    return np.array(samples).transpose(1, 0)

data_sin = np.sin(np.array(range(0, 360, 15)) * np.pi / 180)
data_sins = transpose([data_sin] * 2)

def path(filename):
    return os.path.join('fuzzing_audio_files', filename)

def write_float_sin():
    write(path('sin_441_float.wav'), data_sin, 44100, subtype='FLOAT')
    write(path('sins_441_float.wav'), data_sins, 44100, subtype='FLOAT')
    write(path('sin_96_float.wav'), data_sin, 96000, subtype='FLOAT')
    write(path('sins_96_float.wav'), data_sins, 96000, subtype='FLOAT')

def write_PCM16_sin():
    write(path('sin_441_pcm16.wav'), data_sin, 44100, subtype='PCM_16')
    write(path('sins_441_pcm16.wav'), data_sins, 44100, subtype='PCM_16')
    write(path('sin_96_pcm16.wav'), data_sin, 96000, subtype='PCM_16')
    write(path('sins_96_pcm16.wav'), data_sins, 96000, subtype='PCM_16')

def write_PCM24_sin():
    write(path('sin_441_pcm24.wav'), data_sin, 44100, subtype='PCM_24')
    write(path('sins_441_pcm24.wav'), data_sins, 44100, subtype='PCM_24')
    write(path('sin_96_pcm24.wav'), data_sin, 96000, subtype='PCM_24')
    write(path('sins_96_pcm24.wav'), data_sins, 96000, subtype='PCM_24')

def write_long_sin():
    write(path('sin_long_PCM_16.wav'), np.tile(data_sin, 65536), 44100, subtype='PCM_16')

def write_multichannel_sins():
    write(path('sins_7ch.wav'), transpose([data_sin]*7), 44100, subtype='PCM_32')

def main():
    write_float_sin()
    write_PCM16_sin()
    write_PCM24_sin()
    write_long_sin()
    write_multichannel_sins()

if __name__ == "__main__":
    main()
