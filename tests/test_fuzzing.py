import pytest
import numpy as np
from monolizer import Monolizer

data_sin = (np.sin(np.array(range(0, 360, 15)) * np.pi / 180)).tolist()
data_saw = [i/12 for i in range(-12, 12)]
data_sins = [data_sin] * 2
data_empty = [0] * 24
data_stereo = [data_sin, data_saw]
data_r50 = [data_sin, [i * 0.5 for i in data_sin]]
data_l25 = [[i * 0.25 for i in data_sin], data_sin]
data_r0 = [data_sin, data_empty]

sin = [ 0.00000000e+00, 0.258819045, 0.5, 0.707106781,
             0.866025404, 0.965925826, 1, 0.965925826,
             0.866025404, 0.707106781, 0.5, 0.258819045,
             0.00000000000000012246468,-0.258819045,-0.5,-0.707106781,
            -0.866025404,-0.965925826,-1,-0.965925826,
            -0.866025404,-0.707106781,-0.5,-0.258819045]

@pytest.fixture(params=["sin", "sins", "empty", "sin_tri", "sin_l50", "sin_r25", "sin_r100"])
def fuzzaudiofiles(request):
    return


class TestMonolizerFuzz(object):
    def test_fake_stereo_files(self):
        with Monolizer(file='tests\\fuzzing_audio_files\\sins_441_pcm24.wav') as obj:
            assert obj.channels == 2
            assert obj.isMono
            assert not obj.isEmpty
            assert obj.isFakeStereo

    def test_long_file(self):
        with Monolizer(file='tests\\fuzzing_audio_files\\sin_long_PCM_16.wav') as obj:
            assert obj.channels == 1
            assert obj.isMono
            assert not obj.isEmpty
            assert not obj.isFakeStereo

    def test_multichannel(self):
        with Monolizer(file='tests\\fuzzing_audio_files\\sins_7ch.wav') as obj:
            assert obj.channels == 7
            assert not obj.isMono
            assert not obj.isEmpty
            assert not obj.isFakeStereo
