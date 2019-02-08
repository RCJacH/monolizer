import pytest
from monolizer import FileHandler

class Test_FileHandler(object):
    import os

    def test__init__no_input(self):
        obj = FileHandler()
        assert obj.file == None

    def test__init__file(self):
        obj = FileHandler('tests')
        assert obj.file == None
        obj = FileHandler('tests.wav')
        assert obj.file == "tests.wav"
        obj = FileHandler('tests.Wav')
        assert obj.file == "tests.Wav"
        obj = FileHandler('tests.WAV')
        assert obj.file == "tests.WAV"
        obj = FileHandler('tests.WAVE')
        assert obj.file == "tests.WAVE"

    def test_list_audio_files(self):
        obj = FileHandler('tests')
        print(obj._list_audio_files('tests'))
        assert (set(obj._list_audio_files('tests')) == 
                set(['empty.wav', 'sin.wav', 'sins.wav', 'sin_l50.wav',
                'sin_r25.wav', 'sin_r100.wav', 'sin_tri.wav', 'sinwave.wave']))
