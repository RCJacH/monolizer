"""
Tests for `monolizer` module.
"""
import pytest
import os
import shutil
import numpy as np
from monolizer.monolizer import _SampleblockChannelInfo
from monolizer import Monolizer
from soundfile import read

@pytest.fixture
def tmpdir():
    tmpdir = 'tests\\tmpdir\\'
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    yield tmpdir
    shutil.rmtree(tmpdir)

class Test_SampleblockChannelInfo(object):

    @pytest.fixture
    def obj(self):
        return _SampleblockChannelInfo()

    def test_flag_on_from_sample(self, obj):
        obj.flag = 0
        assert obj.set_flag([[0, 0.5]]) == 2
        obj.flag = 0
        assert obj.set_flag([[-0.25, 0]]) == 1
        obj.flag = 0
        assert obj.set_flag([[0., 0.]]) == 0

    def test_flag_on(self, obj):
        obj.flag = 0
        assert obj.flag == 0
        assert obj.flag_on(1) == 1
        assert obj.flag_on(1) == 1
        assert obj.flag_on(2) == 3
        obj.flag = 0

    def test_transpose(self, obj):
        assert (obj._transpose([[0.1, 0.2], [0.3, 0.6], [0.15, 0.3]]) == [[0.1, 0.3, 0.15], [0.2, 0.6, 0.3]]).all()

    def test_get_ratio(self, obj):
        assert obj._get_ratio([0.5, 0.5]) == 1
        assert obj._get_ratio([0.22900572, 0.11450286]) == 0.5
        assert obj._get_ratio([0., 0.]) == 0

    def test_is_ratio_correlated(self, obj):
        assert obj._is_ratio_correlated([[1], [1]]) == True
        assert obj._is_ratio_correlated([
                                        [0.99990839, 0.99987785, 0.99987783, 0.99984727],
                                        [0.998004  , 0.99800001, 0.99799599, 0.99799196]
                                        ]) == False
        assert obj._is_ratio_correlated([
                                        [1.0148026 , 1.01443943, 1.01423377], 
                                        [1.0148026 , 1.01443943, 1.01423382]
                                        ]) == True

    def test_is_sampleblock_correlated(self, obj):
        assert obj._is_sampleblock_correlated([[0.5, 0.5]] * 3) == True
        assert obj._is_sampleblock_correlated([
                                           [0.00308228, 0.00308228],
                                           [0.00613403, 0.00613403]
                                           ]) == True
        assert obj._is_sampleblock_correlated([
                                            [0.22900572, 0.11450286], 
                                            [0.2323956,  0.1161978 ], 
                                            [0.23575126, 0.11787563], 
                                            [0.23910689, 0.11955345]
                                           ]) == True
        assert obj._is_sampleblock_correlated([
                                           [0.99996948, 0.99996948],
                                           [0.99996948, 0.99804688],
                                           [0.99996948, 0.99609375]
                                           ]) == False
        assert obj._is_sampleblock_correlated([[0., 0.]] * 3) == True

    def test_get_sample_from_sampleblock(self, obj):
        obj.reset_sample()
        assert obj.sample == []
        assert obj._get_sample_from_sampleblock([[0., 0.]] * 3) == []
        assert obj._get_sample_from_sampleblock([
                                   [0.00308228, 0.00308228],
                                   [0.00613403, 0.00613403]
                                   ]) == [0.00308228, 0.00308228]
        assert obj._get_sample_from_sampleblock([
                                   [0.99996948, 0.],
                                   [0.99996948, 0.99804688],
                                   [0.99996948, 0.99609375]
                                   ]) == [0.99996948, 0.99804688]
        obj.reset_sample()

    def test_is_sample_stereo(self, obj):
        assert obj._is_sample_stereo([0.5, 0.3]) == True
        assert obj._is_sample_stereo([0.5]) == False
        assert obj._is_sample_stereo([0.5, 0.5]) == False
        assert obj._is_sample_stereo([0, 0]) == False

class AudioInfo:
    def __init__(self, shape):
        self.src = Monolizer()
        self.src.file = "tests//" + shape + ".wav"
        if shape == "sin":
            self.channel = 0
            self.channels = 1
            self.isMono = True
            self.isEmpty = False
            self.isFakeStereo = False
        if shape == "sins":
            self.channel = 0
            self.channels = 2
            self.isMono = True
            self.isEmpty = False
            self.isFakeStereo = True
        if shape == "empty":
            self.channel = self.src.EMPTY
            self.channels = 1
            self.isMono = False
            self.isEmpty = True
            self.isFakeStereo = False
        if shape == "sin_tri":
            self.channel = self.src.STEREO
            self.channels = 2
            self.isMono = False
            self.isEmpty = False
            self.isFakeStereo = False
        if shape == "sin_l50":
            self.channel = 0
            self.channels = 2
            self.isMono = True
            self.isEmpty = False
            self.isFakeStereo = True
        if shape == "sin_r25":
            self.channel = 1
            self.channels = 2
            self.isMono = True
            self.isEmpty = False
            self.isFakeStereo = True
        if shape == "sin_r100":
            self.channel = 1
            self.channels = 2
            self.isMono = True
            self.isEmpty = False
            self.isFakeStereo = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self.src

@pytest.fixture(params=["sin", "sins", "empty", "sin_tri", "sin_l50", "sin_r25", "sin_r100"])
def audioinfo(request):
    with AudioInfo(request.param) as info:
        yield info

class TestMonolizer(object):

    def test_identify(self):
        obj = Monolizer()
        assert obj._identify_channel(flag=0, eof=True) == obj.EMPTY
        assert obj._identify_channel(flag=0, eof=False) == None
        assert obj._identify_channel(flag=3, correlated=False) == obj.STEREO
        assert obj._identify_channel(flag=3, eof=True) == obj.STEREO
        assert obj._identify_channel(flag=3, correlated=True, eof=False) == None
        assert obj._identify_channel(flag=0, correlated=True, eof=False) == None
        assert obj._identify_channel(flag=1, eof=False, sample=[0.1]) == 0
        assert obj._identify_channel(flag=1, correlated=False, sample=[0.1, 0.2]) == None
        assert obj._identify_channel(flag=1, eof=True, correlated=False) == 0
        assert obj._identify_channel(flag=2, eof=True, correlated=False) == 1
        assert obj._identify_channel(flag=3, eof=True, correlated=True, sample=[0.1, 0.2]) == 1
        assert obj._identify_channel(flag=3, eof=True, correlated=True, sample=[0.5, 0.2]) == 0
        with pytest.raises(Exception):
            obj._identify(flag=3, eof=True, correlated=True, sample=[])
        del obj

    def test_chkMono(self, audioinfo):
        assert audioinfo.src.channel == audioinfo.channel

    def test_isMono(self, audioinfo):
        assert audioinfo.src.isMono == audioinfo.isMono

    def test_isEmpty(self, audioinfo):
        assert audioinfo.src.isEmpty == audioinfo.isEmpty

    def test_isFakeStereo(self, audioinfo):
        assert audioinfo.src.isFakeStereo == audioinfo.isFakeStereo

    def test_monolize(self, tmpdir):
        file = os.path.join(tmpdir, 'sins.wav')
        shutil.copyfile('tests\\sins.wav', file)
        with Monolizer(file=file) as obj:
            obj.monolize()
        compare = read('tests\\sin.wav', always_2d=True)
        result = read(file, always_2d=True)
        assert (x == y for x in compare for y in result)

    def test__str__(self):
        with Monolizer(file='tests\\sin.wav') as obj:
            assert str(obj) == 'tests\\sin.wav\tChannels: 1\t\t\n'
        with Monolizer(file='tests\\sins.wav') as obj:
            assert str(obj) == 'tests\\sins.wav\tChannels: 2\t\tFakeStereo\n'
        with Monolizer(file='tests\\empty.wav') as obj:
            assert str(obj) == 'tests\\empty.wav\tChannels: 1\tEmpty\t\n'
