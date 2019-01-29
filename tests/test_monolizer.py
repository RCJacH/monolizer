"""
Tests for `monolizer` module.
"""
import pytest
from soundfile import SoundFile as sf
from monolizer.monolizer import _SampleblockChannelInfo
from monolizer import Monolizer

class Test_SampleblockChannelInfo(object):

    @classmethod
    def setup_class(cls):
        cls.obj = _SampleblockChannelInfo()

    @classmethod
    def teardown_class(cls):
        del cls.obj

    def test_detect_channel_signal(self):
        self.obj.flag = 0
        assert self.obj.flag_on_from_sample([0, 0.5]) == 2
        self.obj.flag = 0
        assert self.obj.flag_on_from_sample([-0.25, 0]) == 1
        self.obj.flag = 0
        assert self.obj.flag_on_from_sample([0., 0.]) == 0

    def test_flag_on(self):
        self.obj.flag = 0
        obj = _SampleblockChannelInfo()
        assert self.obj.flag == 0
        assert self.obj.flag_on(1) == 1
        assert self.obj.flag_on(1) == 1
        assert self.obj.flag_on(2) == 3
        assert obj.flag == 0
        self.obj.flag = 0

    def test_transpose(self):
        assert (self.obj._transpose([[0.1, 0.2], [0.3, 0.6], [0.15, 0.3]]) == [[0.1, 0.3, 0.15], [0.2, 0.6, 0.3]]).all()

    def test_get_ratio(self):
        assert self.obj.get_ratio([0.5, 0.5]) == 1
        assert self.obj.get_ratio([0.22900572, 0.11450286]) == 0.5
        assert self.obj.get_ratio([0., 0.]) == 0

    def test_is_ratio_correlated(self):
        assert self.obj.is_ratio_correlated([[1], [1]]) == True
        assert self.obj.is_ratio_correlated([
                                            [0.99990839, 0.99987785, 0.99987783, 0.99984727],
                                            [0.998004  , 0.99800001, 0.99799599, 0.99799196]
                                            ]) == False
        assert self.obj.is_ratio_correlated([
                                            [1.0148026 , 1.01443943, 1.01423377], 
                                            [1.0148026 , 1.01443943, 1.01423382]
                                            ]) == True

    def test_is_sampleblock_correlated(self):
        assert self.obj.is_sampleblock_correlated([[0.5, 0.5]] * 3) == True
        assert self.obj.is_sampleblock_correlated([
                                           [0.00308228, 0.00308228],
                                           [0.00613403, 0.00613403]
                                           ]) == True
        assert self.obj.is_sampleblock_correlated([
                                            [0.22900572, 0.11450286], 
                                            [0.2323956,  0.1161978 ], 
                                            [0.23575126, 0.11787563], 
                                            [0.23910689, 0.11955345]
                                           ]) == True
        assert self.obj.is_sampleblock_correlated([
                                           [0.99996948, 0.99996948],
                                           [0.99996948, 0.99804688],
                                           [0.99996948, 0.99609375]
                                           ]) == False
        assert self.obj.is_sampleblock_correlated([[0., 0.]] * 3) == True

    def test_set_sample_from_block(self):
        self.obj.reset_sample()
        assert self.obj.sample == []
        assert self.obj.set_sample_from_sampleblock([[0., 0.]] * 3) == []
        assert self.obj.set_sample_from_sampleblock([
                                   [0.00308228, 0.00308228],
                                   [0.00613403, 0.00613403]
                                   ]) == [0.00308228, 0.00308228]
        self.obj.reset_sample()
        assert self.obj.set_sample_from_sampleblock([
                                   [0.99996948, 0.],
                                   [0.99996948, 0.99804688],
                                   [0.99996948, 0.99609375]
                                   ]) == [0.99996948, 0.99804688]

class TestMonolizer(object):

    @classmethod
    def setup_class(cls):
        cls.obj = Monolizer()

    @classmethod
    def teardown_class(cls):
        del cls.obj

    def test_identify(self):
        assert self.obj._identify(flag=0, eof=True) == self.obj.EMPTY
        assert self.obj._identify(flag=0, eof=False) == None
        assert self.obj._identify(flag=3, correlated=False) == self.obj.STEREO
        assert self.obj._identify(flag=3, eof=True) == self.obj.STEREO
        assert self.obj._identify(flag=3, correlated=True, eof=False) == None
        assert self.obj._identify(flag=0, correlated=True, eof=False) == None
        assert self.obj._identify(flag=1, eof=False, sample=[0.1]) == 0
        assert self.obj._identify(flag=1, correlated=False, sample=[0.1, 0.2]) == None
        assert self.obj._identify(flag=1, eof=True, correlated=False) == 0
        assert self.obj._identify(flag=2, eof=True, correlated=False) == 1
        assert self.obj._identify(flag=3, eof=True, correlated=True, sample=[0.1, 0.2]) == 1
        assert self.obj._identify(flag=3, eof=True, correlated=True, sample=[0.5, 0.2]) == 0
        with pytest.raises(Exception):
            self.obj._identify(flag=3, eof=True, correlated=True, sample=[])
        pass

    def test_monolize(self):
        obj = Monolizer(file='tests\\sin.wav')
        assert obj.monolize() == 0
        obj = Monolizer(file='tests\\sins.wav')
        assert obj.monolize() == 0
        obj = Monolizer(file='tests\\empty.wav')
        assert obj.monolize() == obj.EMPTY
        obj = Monolizer(file='tests\\sin_tri.wav')
        assert obj.monolize() == obj.STEREO
        obj = Monolizer(file='tests\\sin_l50.wav')
        assert obj.monolize() == 0
        obj = Monolizer(file='tests\\sin_r25.wav')
        assert obj.monolize() == 1
        obj = Monolizer(file='tests\\sin_r100.wav')
        assert obj.monolize() == 1
