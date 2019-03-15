"""Classes for analyzing audio and determine their actual channel info.
    _SampleblockChannelInfo is a calculating class that receive sampleblock
information and calculates the ratio between all sample sets of stereo
channels, then returning the channel info of the sampleblock.
    Monolizer is the file handler that takes a file and analyze channel info
of the file, with methods to combine stereo channels into mono channel.
"""

import numpy as np
np.seterr(divide='ignore', invalid='ignore')
from soundfile import SoundFile as sf


class _SampleblockChannelInfo():
    NULL_THRESHOLD = 0.000001 # TODO: get threshold from minimum bit info

    def __init__(self, flag=0, correlated=None, sample=[], sampleblock=None):
        self.flag = flag != None and flag
        self.isCorrelated = correlated
        self.sample = sample != None and sample
        if sampleblock is not None:
            self.set_info(sampleblock)

    def set_info(self, sampleblock):
        self.set_flag(sampleblock)
        self.set_correlation(sampleblock)
        self.set_sample(sampleblock)

    def set_flag(self, sampleblock):
        [self.flag_on(i + 1) for i, v in
         enumerate(self._transpose(sampleblock))
         if (v != 0).any()]
        return self.flag

    def _transpose(self, samples):
        return np.array(samples).transpose(1, 0)

    def flag_on(self, n):
        try:
            self.flag |= 1 << (n - 1)
        except ValueError:
            self.flag = 0
        return self.flag

    def set_correlation(self, sampleblock):
        if self.isCorrelated != False:
            self.isCorrelated = self._is_sampleblock_correlated(sampleblock)

    def _is_sampleblock_correlated(self, sampleblock):
        if len(sampleblock[0]) == 1:
            return True
        ratios = [self._get_ratio(samples) for samples in self._transpose(sampleblock)]
        return self._is_ratio_correlated(ratios)

    def _get_ratio(self, samples):
        a = np.array(samples[:-1])
        b = np.array(samples[1:])
        return np.nan_to_num(np.divide(b, a, dtype='float')).flatten()

    def _is_ratio_correlated(self, ratios):
        return (np.subtract(*ratios).flat < self.NULL_THRESHOLD).all()

    def set_sample(self, sampleblock):
        self.sample = self._get_sample_from_sampleblock(sampleblock)

    def reset_sample(self):
        self.sample = []

    def _get_sample_from_sampleblock(self, sampleblock):
        sample = self.sample
        if not sample or not self._is_sample_stereo(sample):
            sample = self._get_valid_sample(sampleblock)
        return sample

    def _is_sample_stereo(self, sample):
        return len(set(sample)) > 1

    def _get_valid_sample(self, sampleblock):
        try:
            return next((self._validate_sample(samples) for samples in sampleblock if 0 not in samples))
        except StopIteration:
            return []
    
    def _validate_sample(self, samples):
        try:
            return samples.tolist()
        except AttributeError:
            return samples


class Monolizer():
    EMPTY = -2
    STEREO = -1

    def __init__(self, file=None, blocksize=1024, debug=False):
        self.blocksize = blocksize
        self._file = None
        self._filename = file
        self._channel = None
        self._debug = debug
        self._flag = None
        self._correlated = None
        self._sample = None
        if file is not None:
            try:
                self.file = file
            except RuntimeError:
                self.close()

    file = property(lambda self: self._file)

    @file.setter
    def file(self, file):
        self._file = sf(file)
        if self._file.channels <= 2:
            self._channel = self._check_mono()
            self._file.seek(0)

    filename = property(lambda self: self._filename)

    channel = property(lambda self: self._channel)

    channels = property(lambda self: self._file.channels if self.file else 0)

    flag = property(lambda self: self._flag)

    correlated = property(lambda self: self._correlated)

    sample = property(lambda self: self._sample)

    isMono = property(lambda self: self.channel == 1 or self.channel == 0)

    isEmpty = property(lambda self: self.channel == self.EMPTY or self.channels == 0)

    isFakeStereo = property(lambda self: self.isMono and self.channels == 2)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __str__(self):
        empty = self.isEmpty and 'Empty' or ''
        fake = self.isFakeStereo and 'FakeStereo' or ''
        info = "\t".join(
            ["{0.filename}", "Channels: {0.channels}", empty, fake])
        return info.format(self)

    def close(self):
        if self.file:
            self.file.close()
            self._file = None
            self._channel = None

    def _identify_channel(self, flag=0, correlated=False, sample=[], eof=False):
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
        if self._debug:
            self._flag = flag
            self._correlated = correlated
            self._sample = sample
        return None

    def _check_mono(self):
        if self.file:
            flag = correlated = sample = None
            for sampleblock in self.file.blocks(blocksize=self.blocksize, always_2d=True):
                info = _SampleblockChannelInfo(sampleblock=sampleblock,
                                                flag=flag,
                                                correlated=correlated,
                                                sample=sample)
                flag = info.flag
                correlated = info.isCorrelated
                sample = info.sample
                channel = self._identify_channel(flag, correlated, sample)
                if channel is not None:
                    return channel
            return self._identify_channel(flag, correlated, sample, eof=True)
        else:
            return None

    def monolize(self):
        if self.file and self.isMono and self.isFakeStereo:
            data = [x[self.channel] for x in self.file.read()]
            self.file.close()
            with sf(self.filename, 'w', self.file.samplerate, 1,
                   self.file.subtype, self.file.endian,
                   self.file.format, True) as f:
                f.write(data)
            self.file = self.filename
