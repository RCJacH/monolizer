import pytest
# from monolizer import FileHandler
from monolizer.file_handler import _FileInfo


class Test_FileInfo(object):

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

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

# class Test_FileHandler(object):

#     @classmethod
#     def setup_class(cls):
#         pass

#     @classmethod
#     def teardown_class(cls):
#         pass

#     def test_something(self):
#         pass
