import pytest
from monolizer import FileHandler, Monolizer

class Test_FileHandler(object):
    import os

    def test__init__no_input(self):
        obj = FileHandler()
        assert obj.folder == None

    def test__init__file(self):
        obj = FileHandler('tests')
        assert obj.folder == 'tests'

    def test_is_audio_file(self):
        obj = FileHandler()
        assert obj._is_audio_file('tests.wav')
        assert obj._is_audio_file('tests.Wav')
        assert obj._is_audio_file('tests.WAV')
        assert obj._is_audio_file('tests.WAVE')
        assert not obj._is_audio_file('tests.txt')

    def test_list_audio_files(self):
        obj = FileHandler()
        assert (set(obj._list_audio_files('tests')) == 
                set(['empty.wav', 'sin.wav', 'sins.wav', 'sin_l50.wav',
                'sin_r25.wav', 'sin_r100.wav', 'sin_tri.wav', 'sinwave.wave']))

    def test_empty_files(self):
        with FileHandler('tests') as folder:
            assert [f.filename for f in folder.empty_files] == ['tests\\empty.wav']

