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

