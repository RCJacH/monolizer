import numpy as np
np.seterr(divide='ignore', invalid='ignore')
from soundfile import SoundFile as sf
from soundfile import write


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
    EMPTY = -2
    STEREO = -1

    def __init__(self, file=None, blocksize=1024):
        self.blocksize = blocksize
        self._file = None
        self._filename = file
        self._flag = 0
        self._correlated = None
        self._channel = None
        self._sample = []
        if file is not None:
            try:
                self.file = file
            except RuntimeError:
                self.close()

    file = property(lambda self: self._file)

    filename = property(lambda self: self._filename)

    flag = property(lambda self:self._flag)

    correlated = property(lambda self:self._correlated)

    sample = property(lambda self:self._sample)

    channel = property(lambda self: self._channel)

    channels = property(lambda self: self._file.channels if self._file else 0)

    isMono = property(lambda self: self.channel == 1 or self.channel == 0)

    isEmpty = property(lambda self: self.channel == Monolizer.EMPTY)

    isFakeStereo = property(lambda self: self.isMono and self.channels == 2)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __str__(self):
        info = "\n".join(
            ["filename: {0.filename}",
             "channels: {0.channels}",
             "is mono: {0.isMono}",
             "is empty: {0.isEmpty}",
             "is fake stereo: {0.isFakeStereo}"])
        return info.format(self)

    @file.setter
    def file(self, file):
        self._file = sf(file)
        self._setProperties(flag=0, sample=[])
        self._channel = self._chkMono()
        self._file.seek(0)

    def close(self):
        if self.file:
            self.file.close()
            self._file = None
            self._setProperties()
            self._channel = None

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
        self._flag = flag or self.flag
        self._correlated = correlated if self.correlated != False else self.correlated
        self._sample = sample or self.sample

    def _chkSampleblockMono(self, sampleblock):
        info = _SampleblockChannelInfo(sampleblock=sampleblock, flag=self.flag, sample=self.sample)
        info.set_info()
        return info.flag, info.isCorrelated(), info.sample, self.identify()

    def _chkMono(self):
        if self.file:
            for sampleblock in self.file.blocks(blocksize=self.blocksize, always_2d=True):
                flag, correlated, sample, channel = self._chkSampleblockMono(sampleblock)
                self._setProperties(flag, correlated, sample)
                if channel is not None:
                    return channel
            channel = self.identify(eof=True)
            return channel
        else:
            return None

    def writeMono(self, file=None):
        if file and self.isMono:
            data = [x[self.channel] for x in self.file.read()]
            with sf(file, 'w', self.file.samplerate, 1,
                   self.file.subtype, self.file.endian,
                   self.file.format, True) as f:
                f.write(data)
