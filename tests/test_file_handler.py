import pytest
from monolizer import FileHandler
from monolizer.file_handler import _FileInfo


class Test_FileInfo(object):

    def test_FileInfo__init__no_input(self):
        obj = _FileInfo()
        assert obj.file == None
        assert obj.channel == None
        del obj

    def test_init_sin(self):
        obj = _FileInfo(file='tests\\sin.wav')
        assert obj.channel == 0
        assert obj.channels == 1
        assert obj.isMono() == True
        assert obj.toDelete() == False
        assert obj.toMonolize() == False
        del obj

    def test_init_sins(self):
        obj = _FileInfo(file='tests\\sins.wav')
        assert obj.channel == 0
        assert obj.channels == 2
        assert obj.isMono() == True
        assert obj.toDelete() == False
        assert obj.toMonolize() == True
        del obj

    def test_init_empty(self):
        obj = _FileInfo(file='tests\\empty.wav')
        assert obj.channel == obj.EMPTY
        assert obj.channels == 1
        assert obj.isMono() == False
        assert obj.toDelete() == True
        assert obj.toMonolize() == False
        del obj

    def test_init_sin_tri(self):
        obj = _FileInfo(file='tests\\sin_tri.wav')
        assert obj.channel == obj.STEREO
        assert obj.channels == 2
        assert obj.isMono() == False
        assert obj.toDelete() == False
        assert obj.toMonolize() == False
        del obj

    def test_init_sin_l50(self):
        obj = _FileInfo(file='tests\\sin_l50.wav')
        assert obj.channel == 0
        assert obj.channels == 2
        assert obj.isMono() == True
        assert obj.toDelete() == False
        assert obj.toMonolize() == True
        del obj

    def test_init_sin_r25(self):
        obj = _FileInfo(file='tests\\sin_r25.wav')
        assert obj.channel == 1
        assert obj.channels == 2
        assert obj.isMono() == True
        assert obj.toDelete() == False
        assert obj.toMonolize() == True
        del obj

    def test_init_sin_r100(self):
        obj = _FileInfo(file='tests\\sin_r100.wav')
        assert obj.channel == 1
        assert obj.channels == 2
        assert obj.isMono() == True
        assert obj.toDelete() == False
        assert obj.toMonolize() == True
        del obj


class Test_FileHandler(object):
    import os

    def test_FileHandler__init__no_input(self):
        obj = FileHandler()
        assert obj.file == None

    def test_FileHandler__init__file(self):
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

