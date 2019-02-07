import numpy as np
np.seterr(divide='ignore', invalid='ignore')
from soundfile import SoundFile as sf


class _SampleblockChannelInfo():
    NULL_THRESHOLD = 0.000001

    def __init__(self, flag=0, sample=[], sampleblock=None):
        self._channel_flag = flag
        self._isCorrelated = None
        self._sample = sample
        self._sampleblock = sampleblock

    @property
    def flag(self):
        return self._channel_flag

    @flag.setter
    def flag(self, value):
        try:
            self._channel_flag |= 1 << (value - 1)
        except ValueError:
            self._channel_flag = 0

    @property
    def sample(self):
        return self._sample

    def isCorrelated(self):
        return self._isCorrelated

    def _transpose(self, samples):
        return np.array(samples).transpose(1, 0)

    def get_ratio(self, samples):
        a = np.array(samples[:-1])
        b = np.array(samples[1:])
        return np.nan_to_num(np.divide(b, a, dtype='float')).flatten()

    def is_ratio_correlated(self, ratios):
        return (np.subtract(*ratios).flat < self.NULL_THRESHOLD).all()

    def is_sampleblock_correlated(self, sampleblock):
        if len(sampleblock[0]) == 1:
            return True
        ratios = []
        for samples in self._transpose(sampleblock):
            ratios.append(self.get_ratio(samples))
        return self.is_ratio_correlated(ratios)

    def set_correlation(self):
        self._isCorrelated = self.is_sampleblock_correlated(self._sampleblock)

    def flag_on(self, n):
        self.flag = n
        return self.flag

    def flag_on_from_sample(self, samples):
        [self.flag_on(i + 1) for i, v in enumerate(samples) if v != 0]
        return self.flag

    def set_flag(self):
        for samples in self._sampleblock:
            self.flag_on_from_sample(samples)
        return self.flag

    def _validate_sample(self, samples):
        try:
            return samples.tolist()
        except AttributeError:
            return samples

    def get_valid_sample(self, sampleblock):
        try:
            return next((self._validate_sample(samples) for samples in sampleblock if 0 not in samples))
        except StopIteration:
            return []

    def is_sample_stereo(self, sample):
        return len(set(sample)) > 1

    def set_sample_from_sampleblock(self, sampleblock):
        if not self.sample or not self.is_sample_stereo(self.sample):
            self._sample = self.get_valid_sample(sampleblock)
        return self.sample

    def set_sample(self):
        self.set_sample_from_sampleblock(self._sampleblock)

    def reset_sample(self):
        self._sample = []

    def set_info(self):
        self.set_flag()
        self.set_sample()
        self.set_correlation()

class Monolizer():

    def __init__(self, file=None, blocksize=1024):
        self.blocksize = blocksize
        self._file = None
        self.flag = 0
        self.correlated = None
        self.channel = None
        self.channels = None
        self.sample = []
        if file is not None:
            self.file = file

    def __del__(self):
        if self.file:
            self.file.close()

    @classmethod
    def EMPTY(cls):
        return -2

    @classmethod
    def STEREO(cls):
        return -1

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        self._file = sf(file)
        self.flag = 0
        self.sample = []
        self.channel = self.chkMono()
        self._file.seek(0)
        self.channels = self._file.channels

    def _identify(self, flag=0, correlated=False, sample=[], eof=False):
        """
        Possibility for channels
        L == 0; # Empty
        L != 0;
        L == R == 0; # Empty
        L != 0; R == 0; # Channel 0
        L == 0; R != 0; # Channel 1
        L * ratio == R; # Channel = R if ratio > 1 else L
        L * ratio != R; # Stereo
        """
        if flag == 3 and not correlated:
            return self.STEREO
        if sample and len(sample) == 1 and flag&1:
            return 0
        if eof:
            if flag == 0:
                return self.EMPTY
            elif flag < 3:
                return flag - 1
            elif flag == 3:
                try:
                    return sample.index(max(sample, key=abs))
                except IndexError:
                    raise Exception('Sample argument must have at least length of 1.')
        return None

    def identify(self, eof=False):
        return self._identify(flag=self.flag, correlated=self.correlated, sample=self.sample, eof=eof)

    def _setProperties(self, flag=None, correlated=None, sample=None):
        self.flag = flag or self.flag
        self.correlated = correlated if self.correlated != False else self.correlated
        self.sample = sample or self.sample

    def _chkSampleblockMono(self, sampleblock):
        info = _SampleblockChannelInfo(sampleblock=sampleblock, flag=self.flag, sample=self.sample)
        info.set_info()
        return info.flag, info.isCorrelated(), info.sample, self.identify()

    def chkMono(self):
        if self.file:
            for sampleblock in self.file.blocks(blocksize=self.blocksize, always_2d=True):
                flag, correlated, sample, channel = self._chkSampleblockMono(sampleblock)
                self._setProperties(flag, correlated, sample)
                if channel is not None:
                    return channel
            channel = self.identify(eof=True)
            return channel

    def isMono(self):
        return self.channel == 1 or self.channel == 0

    def toDelete(self):
        return self.channel == self.EMPTY

    def toMonolize(self):
        return self.isMono() and self.channels == 2
